from __future__ import annotations

import abc
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from planty.infrastructure.database import raw_async_session_maker
from planty.infrastructure.repositories import (
    ISectionRepository,
    ITaskRepository,
    IUserRepository,
    SQLAlchemySectionRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyUserRepository,
)


class IUnitOfWork(abc.ABC):
    user_repo: IUserRepository
    task_repo: ITaskRepository
    section_repo: ISectionRepository

    async def __aenter__(self) -> IUnitOfWork:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.session_factory = raw_async_session_maker

    async def __aenter__(self) -> IUnitOfWork:
        self.db_session: AsyncSession = self.session_factory()
        self.user_repo = SQLAlchemyUserRepository(self.db_session)
        self.task_repo = SQLAlchemyTaskRepository(self.db_session)
        self.section_repo = SQLAlchemySectionRepository(self.db_session, self.task_repo)
        return await super().__aenter__()

    async def __aexit__(self, *args: Any) -> None:
        await super().__aexit__(*args)
        await self.db_session.close()

    async def commit(self) -> None:
        await self.db_session.commit()

    async def rollback(self) -> None:
        await self.db_session.rollback()
