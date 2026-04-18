import uuid
from core.mail import send_activation_email
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from features.auth.exceptions import (
    InvalidCredentialsError,
    InactiveAccountError,
    InvalidActivationTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from features.auth.model import User
from features.auth.schemas import (
    ActivateRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    RefreshRequest,
    TokenResponse,
    UserResponse,
    evaluate_password,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "role": role, "type": "access", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "type": "refresh", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise InvalidCredentialsError()
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidCredentialsError()
    except jwt.InvalidTokenError:
        raise InvalidCredentialsError()


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        company_name=user.company_name,
        website=user.website,
        role=user.role,
        is_active=user.is_active,
    )


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        result = await self.session.execute(
            select(User).where(User.email == payload.email)
        )
        if result.scalar_one_or_none():
            raise UserAlreadyExistsError(payload.email)

        activation_token = str(uuid.uuid4())

        user = User(
            email=payload.email,
            company_name=payload.company_name,
            website=payload.website,
            hashed_password=_hash_password(payload.password),
            is_active=False,
            activation_token=activation_token,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        strength = evaluate_password(payload.password)

        await send_activation_email(
            email=user.email,
            company_name=user.company_name,
            activation_token=activation_token,
        )

        return RegisterResponse(
            id=user.id,
            email=user.email,
            company_name=user.company_name,
            website=user.website,
            role=user.role,
            is_active=user.is_active,
            password_strength=strength,
            message="Compte créé. Un email d'activation a été envoyé à votre adresse.",
        )

    async def activate(self, payload: ActivateRequest) -> UserResponse:
        result = await self.session.execute(
            select(User).where(User.activation_token == payload.token)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise InvalidActivationTokenError()

        user.is_active = True
        user.activation_token = None
        await self.session.commit()
        await self.session.refresh(user)

        return _to_user_response(user)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        result = await self.session.execute(
            select(User).where(User.email == payload.email)
        )
        user = result.scalar_one_or_none()

        if not user or not _verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveAccountError()

        return TokenResponse(
            access_token=_create_access_token(user.id, user.role),
            refresh_token=_create_refresh_token(user.id),
        )

    async def refresh(self, payload: RefreshRequest) -> TokenResponse:
        data = _decode_token(payload.refresh_token, expected_type="refresh")
        user_id: str = data.get("sub", "")

        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(user_id)

        if not user.is_active:
            raise InactiveAccountError()

        return TokenResponse(
            access_token=_create_access_token(user.id, user.role),
            refresh_token=_create_refresh_token(user.id),
        )

    async def get_current_user(self, token: str) -> UserResponse:
        data = _decode_token(token, expected_type="access")
        user_id: str = data.get("sub", "")

        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(user_id)

        return _to_user_response(user)