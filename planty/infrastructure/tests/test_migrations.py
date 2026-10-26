import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from planty.config import settings
from planty.infrastructure import models  # noqa: F401
from planty.infrastructure.database import Base


def test_migrations_create_current_schema(tmp_path: Path) -> None:
    original_db_name = settings.db_name
    settings.db_name = str(tmp_path / "planty")
    config = Config("alembic.ini")

    try:
        command.upgrade(config, "head")

        seed_environment = os.environ.copy()
        seed_environment.update(
            PLANTY_MODE="DEV",
            PLANTY_DB_NAME=settings.db_name,
        )
        subprocess.run(
            [sys.executable, "-m", "planty.scripts.seed_dev"],
            check=True,
            env=seed_environment,
        )

        engine = create_engine(settings.get_database_url(for_alembic=True))
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            assert compare_metadata(context, Base.metadata) == []

            current_revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            assert (
                current_revision
                == ScriptDirectory.from_config(config).get_current_head()
            )
            counts = connection.execute(
                text(
                    'SELECT (SELECT count(*) FROM "user"), '
                    "(SELECT count(*) FROM section), "
                    "(SELECT count(*) FROM task)"
                )
            ).one()
            assert counts == (2, 14, 18)
    finally:
        settings.db_name = original_db_name
