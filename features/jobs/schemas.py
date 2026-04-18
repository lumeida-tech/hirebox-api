from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, field_validator


class JobCreateRequest(BaseModel):
    title: str
    description: str
    location: str
    skills: List[str]
    is_remote: bool = False
    closes_at: datetime

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        return v.strip()

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Au moins une compétence est requise")
        return v

    @field_validator("closes_at")
    @classmethod
    def validate_closes_at(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("La date de clôture doit être ultérieure à aujourd'hui")
        return v


class JobUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    skills: List[str] | None = None
    is_remote: bool | None = None
    closes_at: datetime | None = None

    @field_validator("closes_at")
    @classmethod
    def validate_closes_at(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("La date de clôture doit être ultérieure à aujourd'hui")
        return v


class JobPublishRequest(BaseModel):
    opens_at: datetime | None = None  # si None, démarre maintenant

    @field_validator("opens_at")
    @classmethod
    def validate_opens_at(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("La date de démarrage doit être dans le futur")
        return v


class JobResponse(BaseModel):
    id: str
    company_id: str
    title: str
    description: str
    location: str
    skills: List[str]
    is_remote: bool
    status: str
    opens_at: datetime | None
    closes_at: datetime
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    total: int
    jobs: List[JobResponse]