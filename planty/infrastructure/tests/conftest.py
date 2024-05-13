from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planty.config import settings
from planty.infrastructure.database import Base, engine, get_async_session


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


@pytest.fixture(scope="function", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # TODO: fill with test data
