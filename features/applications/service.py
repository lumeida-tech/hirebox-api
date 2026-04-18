import io
import uuid
from datetime import timedelta

from minio import Minio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.datastructures import UploadFile

from config.settings import settings
from core.exceptions import NotFoundError
from core.mail import send_application_confirmation_email
from features.applications.model import Application
from features.applications.schemas import ApplicationResponse, ApplicationStatusUpdateRequest
from features.applications.exceptions import ApplicationNotFoundError, ApplicationAccessDeniedError
from features.jobs.model import Job


def _to_response(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        job_id=app.job_id,
        nom=app.nom,
        prenom=app.prenom,
        email=app.email,
        telephone=app.telephone,
        resume_url=app.resume_url,
        introduction_audio_url=app.introduction_audio_url,
        question_on_resume_audio_url=app.question_on_resume_audio_url,
        status=app.status,
        applied_at=app.applied_at,
        updated_at=app.updated_at,
    )


_MAX_AUDIO_SIZE = 2 * 1024 * 1024  # 2 MB
_ALLOWED_AUDIO_EXTENSIONS = (".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".webm")


async def _validate_audio(file: UploadFile) -> None:
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in _ALLOWED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"'{file.filename}' n'est pas un format audio accepté. "
            f"Formats supportés : {', '.join(_ALLOWED_AUDIO_EXTENSIONS)}"
        )

    header = await file.read(4)
    await file.seek(0)

    # MP3 : ID3 tag ou MPEG frame sync
    is_mp3 = header[:3] == b"ID3" or header[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
    # MP4/M4A : 'ftyp' à offset 4
    is_mp4 = len(header) >= 4  # on vérifie ftyp à offset 4 avec plus de bytes
    # WAV : RIFF
    is_wav = header[:4] == b"RIFF"
    # OGG/WebM : OggS ou \x1a\x45
    is_ogg = header[:4] == b"OggS"
    is_webm = header[:2] == b"\x1a\x45"

    if ext == "mp3" and not is_mp3:
        raise ValueError(f"'{file.filename}' n'est pas un fichier MP3 valide.")
    if ext == "wav" and not is_wav:
        raise ValueError(f"'{file.filename}' n'est pas un fichier WAV valide.")


async def _upload_audio(minio: Minio, file: UploadFile, path: str) -> str:
    await _validate_audio(file)
    content = await file.read()

    if len(content) > _MAX_AUDIO_SIZE:
        raise ValueError(f"'{file.filename}' dépasse la taille maximale autorisée (50 MB).")

    minio.put_object(
        settings.MINIO_BUCKET,
        path,
        io.BytesIO(content),
        length=len(content),
        content_type="video/mp4",
    )
    return minio.presigned_get_object(
        settings.MINIO_BUCKET, path, expires=timedelta(hours=24)
    )


class ApplicationService:
    def __init__(self, session: AsyncSession, minio_client: Minio) -> None:
        self.session = session
        self._minio = minio_client

    async def apply(
        self,
        job_id: str,
        nom: str,
        prenom: str,
        email: str,
        telephone: str,
        resume_url: str | None,
        introduction_audio: UploadFile | None,
        question_on_resume_audio: UploadFile | None,
    ) -> ApplicationResponse:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundError(f"Job '{job_id}' introuvable")

        application_id = str(uuid.uuid4())
        intro_url = None
        question_url = None

        if introduction_audio:
            path = f"applications/{job_id}/{application_id}/introduction.mp4"
            intro_url = await _upload_audio(self._minio, introduction_audio, path)

        if question_on_resume_audio:
            path = f"applications/{job_id}/{application_id}/question.mp4"
            question_url = await _upload_audio(self._minio, question_on_resume_audio, path)

        application = Application(
            id=application_id,
            job_id=job_id,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            resume_url=resume_url,
            introduction_audio_url=intro_url,
            question_on_resume_audio_url=question_url,
        )
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)

        await send_application_confirmation_email(
            email=email,
            prenom=prenom,
            nom=nom,
            job_title=job.title,
        )

        return _to_response(application)

    async def get_application(self, application_id: str) -> ApplicationResponse:
        result = await self.session.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            raise ApplicationNotFoundError(application_id)
        return _to_response(app)

    async def list_by_job(self, job_id: str) -> list[ApplicationResponse]:
        result = await self.session.execute(
            select(Application).where(Application.job_id == job_id)
        )
        return [_to_response(a) for a in result.scalars().all()]

    async def update_status(
        self, application_id: str, payload: ApplicationStatusUpdateRequest
    ) -> ApplicationResponse:
        result = await self.session.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            raise ApplicationNotFoundError(application_id)
        app.status = payload.status
        await self.session.commit()
        await self.session.refresh(app)
        return _to_response(app)

    async def withdraw(self, application_id: str, candidate_email: str) -> None:
        result = await self.session.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            raise ApplicationNotFoundError(application_id)
        if app.email != candidate_email:
            raise ApplicationAccessDeniedError()
        await self.session.delete(app)
        await self.session.commit()
