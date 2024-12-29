from typing import Any, AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from planty.config import settings

if settings.mode == "TEST":
    database_url = settings.get_database_url(for_tests=True)
else:
    database_url = settings.get_database_url()


engine = create_async_engine(
    database_url,  # echo=True
)


# Enable foreign key checks for SQLite
if settings.db_type == "sqlite":

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# Ensure to close the session obtained from this sessionmaker
# (or use it as a context manager to automatically handle closure)
raw_async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with raw_async_session_maker() as session:
        yield session
