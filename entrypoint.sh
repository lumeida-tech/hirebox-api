#!/bin/sh
set -e

python -c "
import asyncio
from core.database import Base, engine
from core.migrations import run_schema_migrations
from features.auth.model import User
from features.jobs.model import Job
from features.applications.model import Application, PartialApplication

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    await run_schema_migrations(engine)

asyncio.run(migrate())
"

exec gunicorn app:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 2