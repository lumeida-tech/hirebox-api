from litestar import Controller, post
from litestar.di import Provide

from features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from features.auth.service import AuthService


def provide_auth_service() -> AuthService:
    return AuthService()


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"auth_service": Provide(provide_auth_service, sync_to_thread=False)}

    @post("/register")
    async def register(self, data: RegisterRequest, auth_service: AuthService) -> UserResponse:
        return await auth_service.register(data)

    @post("/login")
    async def login(self, data: LoginRequest, auth_service: AuthService) -> TokenResponse:
        return await auth_service.login(data)
