from typing import Optional

from sqlalchemy import select
from planty.tasks.entities import Task
from planty.tasks.models import TaskModel
from sqlalchemy.orm import Session


# This interface is used in the business layer.
class ITaskRepository:
    def get_task_by_id(self, task_id: int) -> Optional[Task]: ...


# TODO: use `abc` to show that this class implements the interface above
class SQLAlchemyTaskRepository:
    def __init__(self, db_session: Session):
        # TODO: deal with awaits
        self._db_session = db_session

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        task_model = ...
        # task_model = self._db_session.execute(
        #     select(TaskModel).filter(TaskModel.id == task_id)
        # ).one_or_none()
        if task_model:
            # TODO: use mappers?
            return Task(
                id=task_model.id,
                user_id=task_model.user_id,
                section_id=task_model.section_id,
                title=task_model.title,
                description=task_model.description,
                is_completed=task_model.is_completed,
                due_to_next=task_model.due_to_next,
                due_to_days_period=task_model.due_to_days_period,
            )
        return None

    def add_task(self, task: Task) -> None:
        task_model = TaskModel(
            id=task.id,
            user_id=task.user_id,
            section_id=task.section_id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        ...
        # self._db_session.add(task_model)
        # self._db_session.commit()
