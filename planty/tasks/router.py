from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from planty.database import get_async_session
from planty.tasks.entities import Task
from planty.tasks.repositories import SQLAlchemyTaskRepository
from planty.tasks.services import TaskService

router = APIRouter(
    tags=["User tasks"],
)


@router.get("/task/{task_id}")
async def get_task(task_id: int, db_session: Session = Depends(get_async_session)):
    task_repository = SQLAlchemyTaskRepository(db_session)
    task_service = TaskService(task_repository)
    task = task_service.get_task_by_id(task_id)
    if not task:
        # TODO: make specific exceptions
        raise HTTPException(status_code=404, detail="Task not found")
    return task.__dict__


@router.post("/task")
async def create_task(
    task_data: dict, db_session: Session = Depends(get_async_session)
):
    task_repository = SQLAlchemyTaskRepository(db_session)
    task_service = TaskService(task_repository)
    task = Task(**task_data)
    task_service.add_task(task)
    return {"message": "Task created"}
