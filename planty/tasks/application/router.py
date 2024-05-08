from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from planty.tasks.application.schemas import TaskCreateModel
from planty.database import get_async_session
from planty.tasks.domain.entities import Task
from planty.tasks.infrastructure.repositories import SQLAlchemyTaskRepository
from planty.tasks.application.services import TaskService
from planty.utils import generate_uuid

router = APIRouter(
    tags=["User tasks"],
)


def get_task_repository(db_session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyTaskRepository(db_session)


@router.post("/task")
async def create_task(
    task_data: TaskCreateModel,
    # TODO: move to uow
    db_session: AsyncSession = Depends(get_async_session),
):
    repository = get_task_repository(db_session)
    task_service = TaskService(repository)
    task = Task(
        id=generate_uuid(),
        user_id=task_data.user_id,
        section_id=task_data.section_id,
        title=task_data.title,
        description=task_data.description,
        due_to_next=task_data.due_to_next,
        due_to_days_period=task_data.due_to_days_period,
    )
    await task_service.add_task(task)
    # TODO: move to UOW
    await db_session.commit()
    return {"message": "Task created"}
