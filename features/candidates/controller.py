from litestar import Controller, get, post
from litestar.di import Provide
from litestar.params import Parameter, Body
from litestar.enums import RequestEncodingType

from litestar.datastructures import UploadFile

from features.candidates.schemas import (
    CandidateProfileRequest,
    CandidateResponse,
    CVUploadResponse,
    AuthorizationResponse,
)
from features.candidates.service import CandidateService


def provide_candidate_service() -> CandidateService:
    return CandidateService()


class CandidateController(Controller):
    path = "/candidates"
    tags = ["Candidates"]
    dependencies = {"candidate_service": Provide(provide_candidate_service, sync_to_thread=False)}

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
        # TODO: extract user_id from current_user
        return await candidate_service.upsert_profile(user_id="", payload=data)

    @post("/{candidate_id:str}/cv")
    async def upload_cv(
        self,
        candidate_id: str,
        upload_file: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
        candidate_service: CandidateService = Parameter(),
    ) -> CVUploadResponse:
        """Upload un CV au format PDF, parse le texte et le stocke dans MinIO.

        La route attend un `multipart/form-data` avec le champ `upload_file`.
        """
        result = await candidate_service.process_and_store_cv(upload_file=upload_file, candidate_id=candidate_id)
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
        job_id: str | None = Parameter(default=None),
        candidate_service: CandidateService = Parameter(),
    ) -> AuthorizationResponse:
        """Vérifie si la candidature est autorisée pour un candidat (optionnellement pour une offre)."""
        res = await candidate_service.check_authorization(candidate_id=candidate_id, job_id=job_id)
        return AuthorizationResponse(**res)
