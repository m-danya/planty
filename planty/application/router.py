from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from planty.application.schemas import TaskCreateRequest
from planty.application.services import TaskService
from planty.infrastructure.database import get_async_session
from planty.infrastructure.repositories import (
    ITaskRepository,
    IUserRepository,
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


def get_user_repo(
    db_session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return SQLAlchemyUserRepository(db_session)


# TODO: check username = "ab", does the validation work?


@router.post("/task")
async def create_task(
    task_data: TaskCreateRequest,
    db_session: AsyncSession = Depends(get_async_session),
) -> None:
    task_repo = get_task_repo(db_session)
    user_repo = get_user_repo(db_session)
    task_service = TaskService(task_repo=task_repo, user_repo=user_repo)
    await task_service.add_task(task_data)
    # TODO: move to UOW
    await db_session.commit()
    # return {"message": "Task created"}
