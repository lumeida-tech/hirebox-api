from http import HTTPStatus

from litestar import Litestar, get, Response
from litestar.response import Redirect
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme

from core.database import get_async_session
from core.exceptions import EXCEPTION_HANDLERS
from features.auth.controller import AuthController
from features.auth.model import User
from features.jobs.controller import JobController
from features.jobs.model import Job
from features.applications.model import Application, PartialApplication
from features.applications.controller import ApplicationController
from features.candidates.controller import CandidateController
from features.companies.controller import CompanyController


@get("/", include_in_schema=False)
async def root() -> Redirect:
    return Redirect(path="/docs")


@get("/health", tags=["Health"])
async def health_check() -> Response:
    return Response(
        content={"status": "ok", "service": "HireBox API"},
        status_code=HTTPStatus.OK,
    )


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["console"]},
    formatters={"standard": {"format": "%(asctime)s %(levelname)s %(message)s"}},
    log_exceptions="always",
)

logging_middleware = LoggingMiddlewareConfig(
    request_log_fields=["method", "path", "status_code"],
)

app = Litestar(
    middleware=[logging_middleware.middleware],
    logging_config=logging_config,
    request_max_body_size=2 * 1024 * 1024,  # 2 MB

    route_handlers=[
        root,
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
        components=Components(
            security_schemes={
                "BearerAuth": SecurityScheme(
                    type="http",
                    scheme="bearer",
                    bearer_format="JWT",
                )
            }
        ),
        security=[{"BearerAuth": []}],
    ),
)