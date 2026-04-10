from features.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationStatusUpdateRequest,
    ApplicationResponse,
)
from features.applications.exceptions import (
    ApplicationNotFoundError,
    DuplicateApplicationError,
    ApplicationAccessDeniedError,
)


class ApplicationService:
    async def apply(self, payload: ApplicationCreateRequest, candidate_id: str) -> ApplicationResponse:
        raise NotImplementedError

    async def get_application(self, application_id: str, requester_id: str) -> ApplicationResponse:
        raise NotImplementedError

    async def list_by_job(self, job_id: str, requester_id: str) -> list[ApplicationResponse]:
        raise NotImplementedError

    async def list_by_candidate(self, candidate_id: str) -> list[ApplicationResponse]:
        raise NotImplementedError

    async def update_status(
        self, application_id: str, payload: ApplicationStatusUpdateRequest, requester_id: str
    ) -> ApplicationResponse:
        raise NotImplementedError

    async def withdraw(self, application_id: str, candidate_id: str) -> None:
        raise NotImplementedError
