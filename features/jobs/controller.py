from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.params import Parameter

from features.jobs.schemas import JobCreateRequest, JobUpdateRequest, JobResponse
from features.jobs.service import JobService


def provide_job_service() -> JobService:
    return JobService()


class JobController(Controller):
    path = "/jobs"
    tags = ["Jobs"]
    dependencies = {"job_service": Provide(provide_job_service, sync_to_thread=False)}

    @get("/")
    async def list_jobs(
        self,
        job_service: JobService,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> list[JobResponse]:
        return await job_service.list_jobs(page=page, page_size=page_size)

    @get("/{job_id:str}")
    async def get_job(self, job_id: str, job_service: JobService) -> JobResponse:
        return await job_service.get_job(job_id)

    @post("/")
    async def create_job(self, data: JobCreateRequest, job_service: JobService) -> JobResponse:
        # TODO: extract company_id from current_user
        return await job_service.create_job(data, company_id="")

    @patch("/{job_id:str}")
    async def update_job(self, job_id: str, data: JobUpdateRequest, job_service: JobService) -> JobResponse:
        # TODO: extract requester_id from current_user
        return await job_service.update_job(job_id, data, requester_id="")

    @delete("/{job_id:str}", status_code=204)
    async def delete_job(self, job_id: str, job_service: JobService) -> None:
        # TODO: extract requester_id from current_user
        return await job_service.delete_job(job_id, requester_id="")
