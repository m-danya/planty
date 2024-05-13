from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from planty.config import settings

if settings.MODE == "TEST":
    database_url = settings.get_database_url(for_tests=True)
    database_params = {"poolclass": NullPool}
else:
    database_url = settings.get_database_url()
    database_params = {}


engine = create_async_engine(database_url, **database_params)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
