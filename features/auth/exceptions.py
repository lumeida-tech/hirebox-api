from core.exceptions import UnauthorizedError, AlreadyExistsError, NotFoundError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Email ou mot de passe incorrect")


class ExpiredTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Votre session a expiré. Veuillez vous reconnecter.")


class InvalidTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Token invalide. Veuillez vous reconnecter.")


class InvalidTokenTypeError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Type de token incorrect. Utilisez le bon token pour cette opération.")


class InactiveAccountError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Compte non activé. Vérifiez votre boîte email et cliquez sur le lien d'activation.")


class InvalidActivationTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Lien d'activation invalide ou déjà utilisé. Veuillez vous réinscrire.")


class UserAlreadyExistsError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Un compte existe déjà avec l'adresse email '{email}'")


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Utilisateur '{identifier}' introuvable")