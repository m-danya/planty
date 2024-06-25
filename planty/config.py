from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    DB_TYPE: Literal["sqlite", "postgresql"]

    # (if `DB_TYPE` is "sqlite", then only `DB_NAME` is used)

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_NAME: str
    DB_PASS: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_NAME: str
    TEST_DB_PASS: str

    def get_database_url(
        self, for_alembic: bool = False, for_tests: bool = False
    ) -> str:
        # TODO: refactor ifs
        if for_tests:
            if self.DB_TYPE == "postgresql":
                return (
                    "postgresql+asyncpg://"
                    f"{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:"
                    f"{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
                )
            else:
                return f"sqlite+aiosqlite:///{self.TEST_DB_NAME}.db"
        else:
            if self.DB_TYPE == "postgresql":
                return (
                    "postgresql+asyncpg://"
                    f"{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
                    f"{self.DB_PORT}/{self.DB_NAME}"
                )
            else:
                return (
                    f"sqlite+aiosqlite:///{self.DB_NAME}.db"
                    if not for_alembic
                    else f"sqlite+pysqlite:///{self.DB_NAME}.db"
                )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
