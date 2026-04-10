from litestar import Controller, get, post, patch, delete
from litestar.di import Provide

from features.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationStatusUpdateRequest,
    ApplicationResponse,
)
from features.applications.service import ApplicationService


def provide_application_service() -> ApplicationService:
    return ApplicationService()


class ApplicationController(Controller):
    path = "/applications"
    tags = ["Applications"]
    dependencies = {"application_service": Provide(provide_application_service, sync_to_thread=False)}

    @post("/")
    async def apply(self, data: ApplicationCreateRequest, application_service: ApplicationService) -> ApplicationResponse:
        # TODO: extract candidate_id from current_user
        return await application_service.apply(data, candidate_id="")

    @get("/{application_id:str}")
    async def get_application(self, application_id: str, application_service: ApplicationService) -> ApplicationResponse:
        # TODO: extract requester_id from current_user
        return await application_service.get_application(application_id, requester_id="")

    @get("/jobs/{job_id:str}")
    async def list_by_job(self, job_id: str, application_service: ApplicationService) -> list[ApplicationResponse]:
        # TODO: extract requester_id from current_user
        return await application_service.list_by_job(job_id, requester_id="")

    @patch("/{application_id:str}/status")
    async def update_status(
        self, application_id: str, data: ApplicationStatusUpdateRequest, application_service: ApplicationService
    ) -> ApplicationResponse:
        # TODO: extract requester_id from current_user
        return await application_service.update_status(application_id, data, requester_id="")

    @delete("/{application_id:str}/withdraw", status_code=204)
    async def withdraw(self, application_id: str, application_service: ApplicationService) -> None:
        # TODO: extract candidate_id from current_user
        return await application_service.withdraw(application_id, candidate_id="")
