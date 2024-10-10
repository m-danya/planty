from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from planty.config import settings
from planty.infrastructure.database import Base, engine, raw_async_session_maker
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)
from planty.main import app as fastapi_app


@pytest.fixture(scope="function", autouse=True)
async def prepare_database(test_data: dict[str, list[dict[str, Any]]]) -> None:
    assert settings.mode == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with raw_async_session_maker() as session:
        for Model, table_key in [
            (UserModel, "users"),
            (SectionModel, "sections"),
            (TaskModel, "tasks"),
            (AttachmentModel, "attachments"),
        ]:
            for item in test_data[table_key]:
                session.add(Model(**item))

        await session.commit()


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),  # type: ignore
        base_url="http://test",
    ) as ac:
        yield ac
