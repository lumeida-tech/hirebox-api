from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from features.applications.service import ApplicationService


class FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class FakeSession:
    def __init__(self, job_exists: bool = True) -> None:
        self._job_exists = job_exists
        self.added = []

    async def execute(self, _statement):
        job = SimpleNamespace(id="job-1", title="Data Scientist") if self._job_exists else None
        return FakeScalarResult(job)

    def add(self, instance) -> None:
        self.added.append(instance)

    async def commit(self) -> None:
        return None

    async def refresh(self, instance) -> None:
        instance.status = instance.status or "pending"
        now = datetime.now(timezone.utc)
        instance.applied_at = now
        instance.updated_at = now


class DummyMinio:
    pass


@pytest.mark.anyio
async def test_apply_uses_partial_application_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ApplicationService(session=FakeSession(), minio_client=DummyMinio())

    partial = SimpleNamespace(
        id="partial-123",
        person_uid="person-uid-123",
        job_id="job-1",
        nom="Deme",
        prenom="Cheikh",
        email="cheikh@example.com",
        telephone="+221 77 000 00 00",
        cv_obj="cvs/2026/04/W16/19/job-1/cv.pdf",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def fake_get_partial(_partial_id: str):
        return partial

    async def fake_send_email(**_kwargs):
        return None

    monkeypatch.setattr(service, "_get_partial_application_entity", fake_get_partial)
    monkeypatch.setattr("features.applications.service.send_application_confirmation_email", fake_send_email)

    response = await service.apply(
        job_id="job-1",
        nom=None,
        prenom=None,
        email=None,
        telephone=None,
        resume_url=None,
        introduction_audio=None,
        question_on_resume_audio=None,
        partial_application_id="partial-123",
    )

    assert response.job_id == "job-1"
    assert response.nom == "Deme"
    assert response.prenom == "Cheikh"
    assert response.email == "cheikh@example.com"
    assert response.telephone == "+221 77 000 00 00"


@pytest.mark.anyio
async def test_get_partial_application_returns_buffer_data(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ApplicationService(session=FakeSession(), minio_client=DummyMinio())

    partial = SimpleNamespace(
        id="partial-999",
        person_uid="uid-999",
        job_id="job-1",
        nom="Doe",
        prenom="Jane",
        email="jane@example.com",
        telephone="+33 6 11 22 33 44",
        cv_obj="cvs/2026/04/W16/19/job-1/cv.pdf",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def fake_get_partial(_partial_id: str):
        return partial

    monkeypatch.setattr(service, "_get_partial_application_entity", fake_get_partial)

    response = await service.get_partial_application("partial-999")

    assert response.id == "partial-999"
    assert response.person_uid == "uid-999"
    assert response.email == "jane@example.com"
