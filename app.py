from http import HTTPStatus

from litestar import Litestar, get, Response
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from core.exceptions import EXCEPTION_HANDLERS
from features.auth.controller import AuthController
from features.jobs.controller import JobController
from features.applications.controller import ApplicationController
from features.candidates.controller import CandidateController
from features.companies.controller import CompanyController


@get("/health", tags=["Health"])
async def health_check() -> Response:
    return Response(
        content={"status": "ok", "service": "HireBox API"},
        status_code=HTTPStatus.OK,
    )


app = Litestar(
    route_handlers=[
        health_check,
        AuthController,
        JobController,
        ApplicationController,
        CandidateController,
        CompanyController,
    ],
    exception_handlers=EXCEPTION_HANDLERS,
    openapi_config=OpenAPIConfig(
        title="HireBox API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
    ),
)
