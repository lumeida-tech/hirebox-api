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


SHARED_DEPENDENCIES: dict[str, Provide] = {
    "db": Provide(provide_db_session),
    "current_user": Provide(provide_current_user),
}
