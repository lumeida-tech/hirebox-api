from features.candidates.schemas import CandidateProfileRequest, CandidateResponse
from features.candidates.exceptions import CandidateNotFoundError


class CandidateService:
    async def get_profile(self, candidate_id: str) -> CandidateResponse:
        raise NotImplementedError

    async def upsert_profile(self, user_id: str, payload: CandidateProfileRequest) -> CandidateResponse:
        raise NotImplementedError

    async def list_candidates(self, page: int = 1, page_size: int = 20) -> list[CandidateResponse]:
        raise NotImplementedError
