import pytest
from litestar.testing import AsyncTestClient

from app import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncTestClient(app=app) as c:
        yield c
