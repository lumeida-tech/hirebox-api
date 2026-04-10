from core.exceptions import NotFoundError, AlreadyExistsError, ForbiddenError


class CompanyNotFoundError(NotFoundError):
    def __init__(self, company_id: str) -> None:
        super().__init__(f"Company '{company_id}' not found")


class CompanyAlreadyExistsError(AlreadyExistsError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Company '{name}' already exists")


class CompanyAccessDeniedError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__("You do not have permission to modify this company")
