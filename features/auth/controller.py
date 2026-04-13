from litestar import Controller, post
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from features.auth.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
from features.auth.service import AuthService


async def provide_auth_service(db_session: AsyncSession) -> AuthService:
    return AuthService(db_session)


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"auth_service": Provide(provide_auth_service)}

    @post("/register", status_code=201)
    async def register(self, data: RegisterRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.register(data)

    @post("/login")
    async def login(self, data: LoginRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.login(data)

    @post("/refresh")
    async def refresh(self, data: RefreshRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.refresh(data)