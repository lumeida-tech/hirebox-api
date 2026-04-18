#!/bin/sh
set -e

python -c "
import asyncio
from core.database import Base, engine
from features.auth.model import User
from features.jobs.model import Job

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

asyncio.run(migrate())
"

exec gunicorn app:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 2