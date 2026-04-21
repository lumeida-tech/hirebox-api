from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel


class ApplicationStatus(StrEnum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationCreateRequest(BaseModel):
    job_id: str
    cover_letter: str | None = None
    resume_url: str | None = None


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    cover_letter: str | None
    resume_url: str | None
    applied_at: datetime
    updated_at: datetime


class PartialApplicationResponse(BaseModel):
    id: str
    person_uid: str
    job_id: str
    nom: str | None
    prenom: str | None
    email: str | None
    telephone: str | None
    cv_obj: str | None
    created_at: datetime
    updated_at: datetime
