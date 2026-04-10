from core.exceptions import NotFoundError, AlreadyExistsError, ForbiddenError


class ApplicationNotFoundError(NotFoundError):
    def __init__(self, application_id: str) -> None:
        super().__init__(f"Application '{application_id}' not found")


class DuplicateApplicationError(AlreadyExistsError):
    def __init__(self, job_id: str) -> None:
        super().__init__(f"You have already applied to job '{job_id}'")


class ApplicationAccessDeniedError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__("You do not have permission to access this application")
