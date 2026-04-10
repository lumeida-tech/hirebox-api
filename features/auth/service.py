from features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from features.auth.exceptions import InvalidCredentialsError, UserAlreadyExistsError


class AuthService:
    async def register(self, payload: RegisterRequest) -> UserResponse:
        raise NotImplementedError

    async def login(self, payload: LoginRequest) -> TokenResponse:
        raise NotImplementedError

    async def get_current_user(self, token: str) -> UserResponse:
        raise NotImplementedError
