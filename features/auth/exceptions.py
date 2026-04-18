from core.exceptions import UnauthorizedError, AlreadyExistsError, NotFoundError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveAccountError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Compte non activé. Vérifiez votre email pour activer votre compte.")


class InvalidActivationTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Token d'activation invalide ou déjà utilisé.")


class UserAlreadyExistsError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists")


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User '{identifier}' not found")