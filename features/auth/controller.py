from litestar import Controller, post, get
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from features.auth.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, TokenResponse,
    RefreshRequest, ActivateRequest,
    UserResponse,
)
from features.auth.service import AuthService


async def provide_auth_service(db_session: AsyncSession) -> AuthService:
    return AuthService(db_session)


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"auth_service": Provide(provide_auth_service)}

    @post("/register", status_code=201)
    async def register(self, data: RegisterRequest, auth_service: AuthService) -> RegisterResponse:
        return await auth_service.register(data)

    @get("/activate")
    async def activate(
        self,
        auth_service: AuthService,
        token: str = Parameter(query="token"),
    ) -> UserResponse:
        from features.auth.schemas import ActivateRequest
        return await auth_service.activate(ActivateRequest(token=token))

    @post("/login")
    async def login(self, data: LoginRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.login(data)

    @post("/refresh")
    async def refresh(self, data: RefreshRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.refresh(data)