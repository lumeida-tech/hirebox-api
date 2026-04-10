from core.exceptions import NotFoundError, ForbiddenError


class JobNotFoundError(NotFoundError):
    def __init__(self, job_id: str) -> None:
        super().__init__(f"Job '{job_id}' not found")


class JobAccessDeniedError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__("You do not have permission to modify this job")
