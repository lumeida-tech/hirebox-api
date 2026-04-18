import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from features.jobs.model import Job
from features.jobs.schemas import (
    JobCreateRequest, JobUpdateRequest,
    JobPublishRequest, JobResponse, JobListResponse,
)
from features.jobs.exceptions import JobNotFoundError, JobAccessDeniedError


def _to_job_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        description=job.description,
        location=job.location,
        skills=json.loads(job.skills),
        is_remote=job.is_remote,
        status=job.status,
        opens_at=job.opens_at,
        closes_at=job.closes_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


class JobService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_jobs(self, company_id: str, page: int = 1, page_size: int = 20) -> JobListResponse:
        result = await self.session.execute(
            select(Job).where(Job.company_id == company_id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        jobs = result.scalars().all()
        return JobListResponse(
            total=len(jobs),
            jobs=[_to_job_response(j) for j in jobs],
        )

    async def get_job(self, job_id: str) -> JobResponse:
        result = await self.session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(job_id)
        return _to_job_response(job)

    async def create_job(self, payload: JobCreateRequest, company_id: str) -> JobResponse:
        job = Job(
            company_id=company_id,
            title=payload.title,
            description=payload.description,
            location=payload.location,
            skills=json.dumps(payload.skills),
            is_remote=payload.is_remote,
            closes_at=payload.closes_at,
            status="draft",  # toujours draft à la création
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return _to_job_response(job)

    async def publish_job(self, job_id: str, payload: JobPublishRequest, requester_id: str) -> JobResponse:
        result = await self.session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(job_id)
        if job.company_id != requester_id:
            raise JobAccessDeniedError()

        job.opens_at = payload.opens_at or datetime.now(timezone.utc)
        job.status = "open"
        await self.session.commit()
        await self.session.refresh(job)
        return _to_job_response(job)

    async def update_job(self, job_id: str, payload: JobUpdateRequest, requester_id: str) -> JobResponse:
        result = await self.session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(job_id)
        if job.company_id != requester_id:
            raise JobAccessDeniedError()

        if payload.title is not None:
            job.title = payload.title
        if payload.description is not None:
            job.description = payload.description
        if payload.location is not None:
            job.location = payload.location
        if payload.skills is not None:
            job.skills = json.dumps(payload.skills)
        if payload.is_remote is not None:
            job.is_remote = payload.is_remote
        if payload.closes_at is not None:
            job.closes_at = payload.closes_at

        await self.session.commit()
        await self.session.refresh(job)
        return _to_job_response(job)

    async def delete_job(self, job_id: str, requester_id: str) -> None:
        result = await self.session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(job_id)
        if job.company_id != requester_id:
            raise JobAccessDeniedError()
        await self.session.delete(job)
        await self.session.commit()