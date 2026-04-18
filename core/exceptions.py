from http import HTTPStatus
from litestar import Request, Response


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class AppError(Exception):
    """Root exception for all domain errors."""


# ---------------------------------------------------------------------------
# Generic HTTP-mapped errors
# ---------------------------------------------------------------------------

class NotFoundError(AppError):
    pass


class AlreadyExistsError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class ValidationError(AppError):
    pass


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

def not_found_handler(_: Request, exc: NotFoundError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.NOT_FOUND)


def already_exists_handler(_: Request, exc: AlreadyExistsError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.CONFLICT)


def unauthorized_handler(_: Request, exc: UnauthorizedError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.UNAUTHORIZED)


def forbidden_handler(_: Request, exc: ForbiddenError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.FORBIDDEN)


def validation_handler(_: Request, exc: ValidationError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


def value_error_handler(_: Request, exc: ValueError) -> Response:
    return Response(content={"error": str(exc)}, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


EXCEPTION_HANDLERS: dict = {
    NotFoundError: not_found_handler,
    AlreadyExistsError: already_exists_handler,
    UnauthorizedError: unauthorized_handler,
    ForbiddenError: forbidden_handler,
    ValidationError: validation_handler,
    ValueError: value_error_handler,
}
