from litestar import Controller, get, post
from litestar.di import Provide
from litestar.params import Parameter

from features.candidates.schemas import CandidateProfileRequest, CandidateResponse
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
