import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from planty.config import settings
from planty.infrastructure.database import Base, engine, raw_async_session_maker
from planty.infrastructure.models import SectionModel, TaskModel, UserModel
from planty.main import app as fastapi_app


# supports datetimes copied from dbeaver
TEST_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@pytest.fixture(scope="session")
def db_test_data() -> dict[str, list[dict[str, Any]]]:
    return load_json_with_data("db_data.json")


@pytest.fixture(scope="session")
def additional_test_data() -> dict[str, Any]:
    return load_json_with_data("additional_data.json")


def load_json_with_data(filename: str) -> dict[str, Any]:
    with open(Path(__file__).parent / filename) as f:
        test_data: dict[str, Any] = json.load(f)
    for table_key in test_data:
        for row in test_data[table_key]:
            for column in row:
                if row[column] is None:
                    continue
                if column.endswith("_at"):
                    row[column] = datetime.strptime(row[column], TEST_DATETIME_FORMAT)
                if column == "due_to_next" and row[column]:
                    row[column] = datetime.strptime(row[column], "%Y-%m-%d").date()
    test_data["users"].sort(key=lambda x: x.get("id"))
    test_data["sections"].sort(key=lambda x: x.get("id"))
    test_data["tasks"].sort(key=lambda x: x.get("id"))
    # TODO: make this dict immutable to prevent accidental modification
    return test_data


@pytest.fixture(scope="session")
def db_tasks_data(
    db_test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return db_test_data["tasks"]


@pytest.fixture(scope="session")
def db_sections_data(
    db_test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return db_test_data["sections"]


@pytest.fixture(scope="function", autouse=True)
async def prepare_database(db_test_data: dict[str, list[dict[str, Any]]]) -> None:
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with raw_async_session_maker() as session:
        for Model, table_key in [
            (UserModel, "users"),
            (SectionModel, "sections"),
            (TaskModel, "tasks"),
        ]:
            for item in db_test_data[table_key]:
                session.add(Model(**item))

        await session.commit()


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),  # type: ignore
        base_url="http://test",
    ) as ac:
        yield ac
