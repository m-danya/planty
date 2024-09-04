from typing import AsyncGenerator

from sqlalchemy import NullPool, event
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


# Enable foreign key checks for SQLite
if settings.DB_TYPE == "sqlite":

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
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
