import jwt
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from core.config import settings
from core.exceptions import UnauthorizedError


def require_auth(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    auth_header = connection.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Token manquant ou invalide")

    token = auth_header.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise UnauthorizedError("Token invalide")
        connection.state.user_id = payload["sub"]
        connection.state.role = payload.get("role", "")
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expiré")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Token invalide")
