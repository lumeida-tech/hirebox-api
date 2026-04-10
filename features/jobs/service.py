from features.jobs.schemas import JobCreateRequest, JobUpdateRequest, JobResponse
from features.jobs.exceptions import JobNotFoundError, JobAccessDeniedError


class JobService:
    async def list_jobs(self, page: int = 1, page_size: int = 20) -> list[JobResponse]:
        raise NotImplementedError

    async def get_job(self, job_id: str) -> JobResponse:
        raise NotImplementedError

    async def create_job(self, payload: JobCreateRequest, company_id: str) -> JobResponse:
        raise NotImplementedError

    async def update_job(self, job_id: str, payload: JobUpdateRequest, requester_id: str) -> JobResponse:
        raise NotImplementedError

    async def delete_job(self, job_id: str, requester_id: str) -> None:
        raise NotImplementedError
