from core.exceptions import NotFoundError


class CandidateNotFoundError(NotFoundError):
    def __init__(self, candidate_id: str) -> None:
        super().__init__(f"Candidate '{candidate_id}' not found")
