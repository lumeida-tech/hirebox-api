from dataclasses import dataclass
from typing import Annotated

from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Parameter, Body
from litestar.datastructures import UploadFile
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import provide_minio_client
from core.guards import require_auth
from features.applications.schemas import (
    ApplicationStatusUpdateRequest,
    ApplicationResponse,
    PartialApplicationResponse,
)
from features.applications.service import ApplicationService


@dataclass
class ApplicationFormData:
    job_id: str
    nom: str | None = None
    prenom: str | None = None
    email: str | None = None
    telephone: str | None = None
    partial_application_id: str | None = None
    resume_url: str | None = None
    introduction_audio: UploadFile | None = None
    question_on_resume_audio: UploadFile | None = None


def provide_application_service(db_session: AsyncSession, minio_client: Minio) -> ApplicationService:
    return ApplicationService(session=db_session, minio_client=minio_client)


class ApplicationController(Controller):
    path = "/applications"
    tags = ["Applications"]
    dependencies = {
        "minio_client": Provide(provide_minio_client, sync_to_thread=True),
        "application_service": Provide(provide_application_service, sync_to_thread=False),
    }

    @post("/")
    async def apply(
        self,
        data: Annotated[ApplicationFormData, Body(media_type=RequestEncodingType.MULTI_PART)],
        application_service: ApplicationService,
    ) -> ApplicationResponse:
        return await application_service.apply(
            job_id=data.job_id,
            nom=data.nom,
            prenom=data.prenom,
            email=data.email,
            telephone=data.telephone,
            resume_url=data.resume_url,
            introduction_audio=data.introduction_audio,
            question_on_resume_audio=data.question_on_resume_audio,
            partial_application_id=data.partial_application_id,
        )

    @get("/partial/{partial_application_id:str}")
    async def get_partial_application(
        self,
        partial_application_id: str,
        application_service: ApplicationService,
    ) -> PartialApplicationResponse:
        return await application_service.get_partial_application(partial_application_id)

    @get("/{application_id:str}", guards=[require_auth])
    async def get_application(
        self, application_id: str, application_service: ApplicationService
    ) -> ApplicationResponse:
        return await application_service.get_application(application_id)

    @get("/jobs/{job_id:str}", guards=[require_auth])
    async def list_by_job(
        self, job_id: str, application_service: ApplicationService
    ) -> list[ApplicationResponse]:
        return await application_service.list_by_job(job_id)

    @patch("/{application_id:str}/status", guards=[require_auth])
    async def update_status(
        self,
        application_id: str,
        data: ApplicationStatusUpdateRequest,
        application_service: ApplicationService,
    ) -> ApplicationResponse:
        return await application_service.update_status(application_id, data)

    @delete("/{application_id:str}/withdraw", status_code=204)
    async def withdraw(
        self,
        application_id: str,
        application_service: ApplicationService,
        candidate_email: str = Parameter(),
    ) -> None:
        return await application_service.withdraw(application_id, candidate_email)
