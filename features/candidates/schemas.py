from pydantic import BaseModel


class CandidateProfileRequest(BaseModel):
    bio: str | None = None
    skills: list[str] = []
    years_of_experience: int | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None


class CandidateResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    bio: str | None
    skills: list[str]
    years_of_experience: int | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
