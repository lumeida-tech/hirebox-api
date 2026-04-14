"""
Shared Litestar dependencies (DB session, current user, etc.).
Each feature can inject these via `dependencies=` on its controller.
"""
from litestar.di import Provide


# Placeholder — replace with your actual DB session factory (e.g. SQLAlchemy async)
async def provide_db_session():
    raise NotImplementedError("Wire up your database session here")


# Placeholder — replace with your JWT / session auth logic
async def provide_current_user():
    raise NotImplementedError("Wire up current user extraction here")


# MinIO provider
from minio import Minio
from config.settings import settings


def provide_minio_client() -> Minio:
    """Create a MinIO client and ensure the main bucket exists."""
    client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )
    try:
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)
    except Exception:
        # Best effort: don't crash the app here. Errors will surface when using the client.
        pass

    return client


SHARED_DEPENDENCIES: dict[str, Provide] = {
    "db": Provide(provide_db_session),
    "current_user": Provide(provide_current_user),
    # MinIO client is created synchronously and may perform blocking IO; run it in a thread.
    "minio_client": Provide(provide_minio_client, sync_to_thread=True),
}
