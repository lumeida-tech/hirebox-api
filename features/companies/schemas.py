from pydantic import BaseModel, HttpUrl


class CompanyCreateRequest(BaseModel):
    name: str
    description: str | None = None
    website: HttpUrl | None = None
    industry: str | None = None
    size: str | None = None  # e.g. "1-10", "11-50", "51-200"
    location: str | None = None


class CompanyUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    website: HttpUrl | None = None
    industry: str | None = None
    size: str | None = None
    location: str | None = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    description: str | None
    website: str | None
    industry: str | None
    size: str | None
    location: str | None
    owner_id: str
