from datetime import datetime
from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    title: str
    description: str
    location: str
    salary_min: int | None = None
    salary_max: int | None = None
    is_remote: bool = False


class JobUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    is_remote: bool | None = None


class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    location: str
    salary_min: int | None
    salary_max: int | None
    is_remote: bool
    company_id: str
    created_at: datetime
    updated_at: datetime
