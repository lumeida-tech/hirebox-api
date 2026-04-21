from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass(frozen=True)
class MigrationStep:
    identifier: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[MigrationStep, ...] = (
    MigrationStep(
        identifier="20260421_add_company_name_to_users",
        statements=(
            "ALTER TABLE IF EXISTS users "
            "ADD COLUMN IF NOT EXISTS company_name VARCHAR(255) NOT NULL DEFAULT ''",
        ),
    ),
)


async def run_schema_migrations(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )

        result = await connection.execute(text("SELECT id FROM schema_migrations"))
        applied_migrations = {row[0] for row in result.fetchall()}

        for migration in MIGRATIONS:
            if migration.identifier in applied_migrations:
                continue

            for statement in migration.statements:
                await connection.execute(text(statement))

            await connection.execute(
                text("INSERT INTO schema_migrations (id) VALUES (:id)"),
                {"id": migration.identifier},
            )
