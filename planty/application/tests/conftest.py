from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from planty.application.auth import current_user
from planty.domain.task import User

from planty.infrastructure.database import Base, engine, raw_async_session_maker
from planty.infrastructure.models import (
    SectionModel,
    TaskModel,
    UserModel,
)
from planty.main import app as fastapi_app


@pytest.fixture(scope="function", autouse=True)
async def prepare_database(test_data: dict[str, list[dict[str, Any]]]) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with raw_async_session_maker() as session:
        for Model, table_key in [
            (UserModel, "users"),
            (SectionModel, "sections"),
            (TaskModel, "tasks"),
        ]:
            for item in test_data[table_key]:
                session.add(Model(**item))

        await session.commit()


@pytest.fixture(scope="function")  # because of the override
async def ac(test_user: User) -> AsyncGenerator[AsyncClient, None]:
    # Mock `current_user` with `test_user`:
    fastapi_app.dependency_overrides[current_user] = lambda: test_user
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(scope="function")  # because of the override
async def ac_another_user(another_test_user: User) -> AsyncGenerator[AsyncClient, None]:
    # Mock `current_user` with `another_test_user`:
    fastapi_app.dependency_overrides[current_user] = lambda: another_test_user
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
    ) as ac:
        yield ac
