from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from planty.tasks.application.schemas import TaskCreateModel
from planty.database import get_async_session
from planty.tasks.infrastructure.repositories import (
    ITaskRepository,
    SQLAlchemyTaskRepository,
)
from planty.tasks.application.services import TaskService

router = APIRouter(
    tags=["User tasks"],
)


def get_task_repository(
    db_session: AsyncSession = Depends(get_async_session),
) -> ITaskRepository:
    return SQLAlchemyTaskRepository(db_session)


@router.post("/task")
async def create_task(
    task_data: TaskCreateModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    repository = get_task_repository(db_session)
    task_service = TaskService(repository)
    await task_service.add_task(task_data)
    # TODO: move to UOW
    await db_session.commit()
    return {"message": "Task created"}
