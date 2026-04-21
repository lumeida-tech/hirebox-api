from pydantic import BaseModel, Field


class CandidateProfileRequest(BaseModel):
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
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


class CVUploadResponse(BaseModel):
    candidate_id: str
    cv_url: str
    preview: str | None = None
    pages: int | None = None
    size_bytes: int | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    telephone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experiences: list[str] = Field(default_factory=list)
    partial_application_id: str | None = None
    person_uid: str | None = None
    ai_question: str | None = None


class AuthorizationResponse(BaseModel):
    candidate_id: str
    authorized: bool
    reason: str | None = None
