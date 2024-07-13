from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from planty.application.schemas import (
    SectionCreateRequest,
    TaskCreateRequest,
)
from planty.application.services import SectionService, TaskService
from planty.infrastructure.database import get_async_session
from planty.infrastructure.repositories import (
    ISectionRepository,
    ITaskRepository,
    IUserRepository,
    SQLAlchemySectionRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyUserRepository,
)

router = APIRouter(
    tags=["User tasks"],
)


def get_task_repo(
    db_session: AsyncSession = Depends(get_async_session),
) -> ITaskRepository:
    return SQLAlchemyTaskRepository(db_session)


def get_section_repo(
    db_session: AsyncSession = Depends(get_async_session),
    task_repo: ITaskRepository = Depends(get_task_repo),
) -> ISectionRepository:
    return SQLAlchemySectionRepository(db_session, task_repo)


def get_user_repo(
    db_session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return SQLAlchemyUserRepository(db_session)


# TODO: check username = "ab", does the validation work?


@router.post("/task")
async def create_task(
    task_data: TaskCreateRequest,
    db_session: AsyncSession = Depends(get_async_session),
) -> Any:  # TODO: add validation
    task_repo = get_task_repo(db_session)
    user_repo = get_user_repo(db_session)
    task_service = TaskService(task_repo=task_repo, user_repo=user_repo)
    await task_service.add_task(task_data)
    # TODO: move to UOW
    await db_session.commit()
    return {"message": "Task created"}


@router.post("/section")
async def create_section(
    section_data: SectionCreateRequest,
    db_session: AsyncSession = Depends(get_async_session),
) -> Any:  # TODO: add validation
    task_repo = get_task_repo(db_session)
    section_repo = get_section_repo(db_session)  # WRONG
    section_service = SectionService(section_repo, task_repo)
    section = await section_service.add(section_data)
    # TODO: move to UOW
    await db_session.commit()
    return {"message": "Session created", "id": section.id}


@router.get("/section/{section_id}")
async def get_section(
    section_id: UUID,
    db_session: AsyncSession = Depends(get_async_session),
    section_repo: ISectionRepository = Depends(get_section_repo),
) -> Any:  # TODO: add validation
    # TODO: implement UOW, deal with possible sessions problems above
    task_repo = get_task_repo(db_session)
    section_service = SectionService(section_repo, task_repo)
    section = await section_service.get_section(section_id)
    return section
