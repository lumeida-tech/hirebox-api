from __future__ import annotations

import io
from datetime import datetime, timezone

import pytest

from features.candidates.service import CandidateService


class DummyMinio:
    def __init__(self) -> None:
        self.last_put: tuple[str, str, int] | None = None

    def put_object(self, bucket: str, obj: str, file_obj: io.BytesIO, size: int) -> None:
        self.last_put = (bucket, obj, size)

    def presigned_get_object(self, bucket: str, obj: str, expires) -> str:
        return f"https://minio.local/{bucket}/{obj}"


class FakeUploadFile:
    def __init__(self, content: bytes, filename: str = "cv.pdf") -> None:
        self.filename = filename
        self.file = io.BytesIO(content)

    async def read(self, n: int = -1) -> bytes:
        return self.file.read(n)

    async def seek(self, offset: int) -> None:
        self.file.seek(offset)


class FakeDbSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.committed = False

    def add(self, instance: object) -> None:
        self.added.append(instance)

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.anyio
async def test_extract_structured_fields_with_sections() -> None:
    service = CandidateService(minio_client=DummyMinio())
    raw_text = """
John Doe
Paris, France
john.doe@example.com

Skills
Python, Docker, AWS
FastAPI; SQL

Experiences
Acme Corp - Senior Engineer (2019-2022): Built APIs and mentored team.
Globex - Engineer (2017-2019): Migrated legacy services.
""".strip()

    fields = service._extract_structured_fields(raw_text)

    assert fields["full_name"] == "John Doe"
    assert fields["first_name"] == "John"
    assert fields["last_name"] == "Doe"
    assert fields["email"] == "john.doe@example.com"
    assert "Python" in fields["skills"]
    assert "Docker" in fields["skills"]
    assert len(fields["experiences"]) >= 1


@pytest.mark.anyio
async def test_extract_structured_fields_fallback_keywords_and_years() -> None:
    service = CandidateService(minio_client=DummyMinio())
    raw_text = """
Jane Smith
Backend engineer with strong focus on python and kubernetes.
Worked at Contoso from 2018 to 2021 on cloud modernization.
Then joined Fabrikam in 2022 to lead platform initiatives.
""".strip()

    fields = service._extract_structured_fields(raw_text)

    assert fields["full_name"] == "Jane Smith"
    assert "Python" in fields["skills"]
    assert "Kubernetes" in fields["skills"]
    assert any("2018" in item or "2022" in item for item in fields["experiences"])


def test_build_dated_cv_object_path_uses_iso_week() -> None:
    fixed = datetime(2026, 4, 19, 10, 0, tzinfo=timezone.utc)

    path = CandidateService._build_dated_cv_object_path("job-123", fixed)

    assert path == "cvs/2026/04/W16/19/job-123/cv.pdf"


@pytest.mark.anyio
async def test_process_and_store_cv_returns_structured_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    minio = DummyMinio()
    service = CandidateService(minio_client=minio)
    upload = FakeUploadFile(content=b"%PDF-1.4 fake")

    async def fake_validate(_upload_file):
        return True

    async def fake_parse(_upload_file):
        return "John Doe\nSkills\nPython, Docker\nExperiences\nAcme 2019-2022"

    monkeypatch.setattr(service, "_validate_pdf", fake_validate)
    monkeypatch.setattr(service, "_parse_pdf", fake_parse)
    monkeypatch.setattr(
        service,
        "_build_dated_cv_object_path",
        lambda _candidate_id: "cvs/2026/04/W16/19/job-123/cv.pdf",
    )

    result = await service.process_and_store_cv(upload_file=upload, candidate_id="job-123")

    assert minio.last_put == ("hirebox-cvs", "cvs/2026/04/W16/19/job-123/cv.pdf", len(b"%PDF-1.4 fake"))
    assert result["candidate_id"] == "job-123"
    assert result["full_name"] == "John Doe"
    assert "Python" in result["skills"]
    assert "Acme 2019-2022" in result["experiences"]


@pytest.mark.anyio
async def test_process_and_store_cv_creates_partial_application(monkeypatch: pytest.MonkeyPatch) -> None:
    minio = DummyMinio()
    session = FakeDbSession()
    service = CandidateService(minio_client=minio)
    upload = FakeUploadFile(content=b"%PDF-1.4 fake")

    async def fake_validate(_upload_file):
        return True

    async def fake_parse(_upload_file):
        return "John Doe\njohn.doe@example.com\n+33 6 12 34 56 78\nSkills\nPython"

    monkeypatch.setattr(service, "_validate_pdf", fake_validate)
    monkeypatch.setattr(service, "_parse_pdf", fake_parse)
    monkeypatch.setattr(
        service,
        "_build_dated_cv_object_path",
        lambda _candidate_id: "cvs/2026/04/W16/19/job-123/cv.pdf",
    )

    result = await service.process_and_store_cv(
        upload_file=upload,
        candidate_id="job-123",
        db_session=session,
    )

    assert session.committed is True
    assert len(session.added) == 1
    assert result["partial_application_id"] is not None
    assert result["person_uid"] is not None
    assert result["email"] == "john.doe@example.com"
