from dataclasses import dataclass
from typing import Annotated

from litestar import Controller, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Parameter, Body
from litestar.datastructures import UploadFile
from minio import Minio

from core.dependencies import provide_minio_client
from core.guards import require_auth
from features.candidates.schemas import (
    CandidateProfileRequest,
    CandidateResponse,
    CVUploadResponse,
    AuthorizationResponse,
)
from features.candidates.service import CandidateService


@dataclass
class CVUploadData:
    cv: UploadFile


def provide_candidate_service(minio_client: Minio) -> CandidateService:
    return CandidateService(minio_client=minio_client)


class CandidateController(Controller):
    path = "/candidates"
    tags = ["Candidates"]
    guards = [require_auth]
    dependencies = {
        "minio_client": Provide(provide_minio_client, sync_to_thread=True),
        "candidate_service": Provide(provide_candidate_service, sync_to_thread=False),
    }

    @get("/")
    async def list_candidates(
        self,
        candidate_service: CandidateService,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> list[CandidateResponse]:
        return await candidate_service.list_candidates(page=page, page_size=page_size)

    @get("/{candidate_id:str}")
    async def get_candidate(self, candidate_id: str, candidate_service: CandidateService) -> CandidateResponse:
        return await candidate_service.get_profile(candidate_id)

    @post("/me")
    async def upsert_my_profile(
        self, data: CandidateProfileRequest, candidate_service: CandidateService
    ) -> CandidateResponse:
        return await candidate_service.upsert_profile(user_id="", payload=data)

    @post("/{candidate_id:str}/cv")
    async def upload_cv(
        self,
        candidate_id: str,
        data: Annotated[CVUploadData, Body(media_type=RequestEncodingType.MULTI_PART)],
        candidate_service: CandidateService,
    ) -> CVUploadResponse:
        result = await candidate_service.process_and_store_cv(
            upload_file=data.cv, candidate_id=candidate_id
        )
        return CVUploadResponse(
            candidate_id=result["candidate_id"],
            cv_url=result["cv_url"],
            preview=result.get("preview"),
            pages=result.get("pages"),
            size_bytes=result.get("size_bytes"),
            ai_question=result.get("ai_question"),
        )

    @get("/{candidate_id:str}/authorize")
    async def authorize_candidate(
        self,
        candidate_id: str,
        candidate_service: CandidateService,
        job_id: str | None = Parameter(default=None),
    ) -> AuthorizationResponse:
        res = await candidate_service.check_authorization(candidate_id=candidate_id, job_id=job_id)
        return AuthorizationResponse(**res)
