from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planty.infrastructure.database import get_async_session


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session
