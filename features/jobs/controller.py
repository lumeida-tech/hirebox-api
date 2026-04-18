from litestar import Controller, get, post, patch, delete, Request
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from core.guards import require_auth
from features.jobs.schemas import (
    JobCreateRequest, JobUpdateRequest,
    JobPublishRequest, JobResponse, JobListResponse,
)
from features.jobs.service import JobService


async def provide_job_service(db_session: AsyncSession) -> JobService:
    return JobService(db_session)


class JobController(Controller):
    path = "/jobs"
    tags = ["Jobs"]
    guards = [require_auth]
    dependencies = {"job_service": Provide(provide_job_service)}

    @get("/")
    async def list_jobs(
        self,
        request: Request,
        job_service: JobService,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> JobListResponse:
        company_id = request.state.user_id
        return await job_service.list_jobs(company_id=company_id, page=page, page_size=page_size)

    @get("/{job_id:str}")
    async def get_job(self, job_id: str, job_service: JobService) -> JobResponse:
        return await job_service.get_job(job_id)

    @post("/", status_code=201)
    async def create_job(
        self, request: Request, data: JobCreateRequest, job_service: JobService
    ) -> JobResponse:
        company_id = request.state.user_id
        return await job_service.create_job(data, company_id=company_id)

    @post("/{job_id:str}/publish")
    async def publish_job(
        self, job_id: str, request: Request, data: JobPublishRequest, job_service: JobService
    ) -> JobResponse:
        requester_id = request.state.user_id
        return await job_service.publish_job(job_id, data, requester_id=requester_id)

    @patch("/{job_id:str}")
    async def update_job(
        self, job_id: str, request: Request, data: JobUpdateRequest, job_service: JobService
    ) -> JobResponse:
        requester_id = request.state.user_id
        return await job_service.update_job(job_id, data, requester_id=requester_id)

    @delete("/{job_id:str}", status_code=204)
    async def delete_job(
        self, job_id: str, request: Request, job_service: JobService
    ) -> None:
        requester_id = request.state.user_id
        await job_service.delete_job(job_id, requester_id=requester_id)