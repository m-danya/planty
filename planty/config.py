import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PARALLEL_DBS_PREFIX = "planty_test_random_"


class Settings(BaseSettings):
    mode: Literal["DEV", "TEST", "PROD"]

    aws_url: str
    aws_secret_access_key: str
    aws_access_key_id: str
    aws_attachments_bucket: str

    db_type: Literal["sqlite", "postgresql"]

    # (if `DB_TYPE` is "sqlite", then only `DB_NAME` is used)

    db_host: str
    db_port: int
    db_user: str
    db_name: str
    db_pass: str

    test_db_host: str
    test_db_port: int
    test_db_user: str
    test_db_name: str  # isn't used for sqlite (hardcoded to :memory:)
    test_db_pass: str

    def get_database_url(
        self, for_alembic: bool = False, for_tests: bool = False
    ) -> str:
        # TODO: refactor ifs
        if for_tests:
            if self.db_type == "postgresql":
                return (
                    "postgresql+asyncpg://"
                    f"{self.test_db_user}:{self.test_db_pass}@{self.test_db_host}:"
                    f"{self.test_db_port}/{self.test_db_name}"
                )
            else:
                # Uncomment to get database with sample data
                # return f"sqlite+aiosqlite:///{self.test_db_name}.db"

                # In-memory database. Make sure to use one connection (do not
                # disable connection pooling), as `?cache=shared` doesn't seem to
                # work here (set poolclass to NullPull and tests will fail)
                return "sqlite+aiosqlite:///:memory:?cache=shared"
        else:
            if self.db_type == "postgresql":
                return (
                    "postgresql+asyncpg://"
                    f"{self.db_user}:{self.db_pass}@{self.db_host}:"
                    f"{self.db_port}/{self.db_name}"
                )
            else:
                return (
                    f"sqlite+aiosqlite:///{self.db_name}.db"
                    if not for_alembic
                    else f"sqlite+pysqlite:///{self.db_name}.db"
                )

    auth_secret: str

    # TODO: should the default value be `True`?
    shutdown_containers_after_test: bool = False

    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("PLANTY_MODE") == "PROD" else ".env.dev",
        extra="ignore",
        env_prefix="PLANTY_",
    )


settings = Settings()
