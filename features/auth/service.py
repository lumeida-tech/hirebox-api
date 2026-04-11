from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from features.auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from features.auth.model import User
from features.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise InvalidCredentialsError()
    except jwt.InvalidTokenError:
        raise InvalidCredentialsError()


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, payload: RegisterRequest) -> UserResponse:
        result = await self.session.execute(
            select(User).where(User.email == payload.email)
        )
        if result.scalar_one_or_none():
            raise UserAlreadyExistsError(payload.email)

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=_hash_password(payload.password),
        )
        self.session.add(user)
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

        token = _create_access_token(user.id, user.role)
        return TokenResponse(access_token=token)

    async def get_current_user(self, token: str) -> UserResponse:
        payload = _decode_token(token)
        user_id: str = payload.get("sub", "")

        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(user_id)

        return _to_user_response(user)