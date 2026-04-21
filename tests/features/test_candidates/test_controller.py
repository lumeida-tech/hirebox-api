from __future__ import annotations

import io

import pytest

from features.candidates.controller import CandidateController, CVUploadData


class FakeUploadFile:
    def __init__(self) -> None:
        self.filename = "cv.pdf"
        self.file = io.BytesIO(b"%PDF-1.4 fake")


class FakeQueryResult:
    def __init__(self, value) -> None:
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class FakeDbSession:
    async def execute(self, _statement):
        return FakeQueryResult(object())


class FakeCandidateService:
    async def process_and_store_cv(self, upload_file, candidate_id: str, db_session=None):
        return {
            "candidate_id": candidate_id,
            "cv_url": "https://minio.local/hirebox-cvs/cvs/2026/04/W16/19/job-123/cv.pdf",
            "preview": "John Doe profile",
            "pages": 1,
            "size_bytes": 1234,
            "full_name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "telephone": "+33 6 12 34 56 78",
            "skills": ["Python", "Docker"],
            "experiences": ["Acme Corp (2019-2022)"],
            "partial_application_id": "partial-123",
            "person_uid": "person-uid-123",
            "ai_question": "Pouvez-vous decrire un projet Python ?",
        }


@pytest.mark.anyio
async def test_upload_cv_endpoint_returns_structured_fields() -> None:
    controller = object.__new__(CandidateController)

    response = await CandidateController.upload_cv.fn(
        controller,
        job_id="job-123",
        data=CVUploadData(cv=FakeUploadFile()),
        candidate_service=FakeCandidateService(),
        db_session=FakeDbSession(),
    )

    assert response.candidate_id == "job-123"
    assert response.full_name == "John Doe"
    assert response.first_name == "John"
    assert response.last_name == "Doe"
    assert response.email == "john.doe@example.com"
    assert response.telephone == "+33 6 12 34 56 78"
    assert "Python" in response.skills
    assert response.experiences == ["Acme Corp (2019-2022)"]
    assert response.partial_application_id == "partial-123"
