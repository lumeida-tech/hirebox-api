from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, EmailStr


class ApplicationStatus(StrEnum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    nom: str
    prenom: str
    email: str
    telephone: str
    resume_url: str | None
    introduction_audio_url: str | None
    question_on_resume_audio_url: str | None
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime
