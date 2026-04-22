from http import HTTPStatus
from litestar import Request, Response
from litestar.exceptions import ValidationException


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


def litestar_validation_handler(_: Request, exc: ValidationException) -> Response:
    errors = []
    if hasattr(exc, "extra") and exc.extra:
        for item in exc.extra:
            if isinstance(item, dict):
                message = item.get("message", "")
                field = item.get("key", "")
                if field:
                    errors.append(f"{field}: {message}")
                else:
                    errors.append(message)
    if not errors:
        errors = [str(exc.detail) if hasattr(exc, "detail") else str(exc)]
    return Response(
        content={"errors": errors},
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )


EXCEPTION_HANDLERS: dict = {
    NotFoundError: not_found_handler,
    AlreadyExistsError: already_exists_handler,
    UnauthorizedError: unauthorized_handler,
    ForbiddenError: forbidden_handler,
    ValidationError: validation_handler,
    ValueError: value_error_handler,
    ValidationException: litestar_validation_handler,
}