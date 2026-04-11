from http import HTTPStatus

from litestar import Litestar, get, Response
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from core.database import Base, engine, get_async_session
from core.exceptions import EXCEPTION_HANDLERS
from features.auth.controller import AuthController
from features.auth.model import User  # enregistre le model dans Base
from features.jobs.controller import JobController
from features.applications.controller import ApplicationController
from features.candidates.controller import CandidateController
from features.companies.controller import CompanyController


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@get("/health", tags=["Health"])
async def health_check() -> Response:
    return Response(
        content={"status": "ok", "service": "HireBox API"},
        status_code=HTTPStatus.OK,
    )


app = Litestar(
    on_startup=[create_tables],
    route_handlers=[
        health_check,
        AuthController,
        JobController,
        ApplicationController,
        CandidateController,
        CompanyController,
    ],
    dependencies={"db_session": Provide(get_async_session)},
    exception_handlers=EXCEPTION_HANDLERS,
    openapi_config=OpenAPIConfig(
        title="HireBox API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
    ),
)