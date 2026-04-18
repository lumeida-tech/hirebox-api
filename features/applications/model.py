import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String, nullable=False)
    prenom: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    telephone: Mapped[str] = mapped_column(String, nullable=False)
    resume_url: Mapped[str | None] = mapped_column(String, nullable=True)
    introduction_audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    question_on_resume_audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    job: Mapped["Job"] = relationship("Job", back_populates="applications")


from features.jobs.model import Job  # noqa: E402
Job.applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
