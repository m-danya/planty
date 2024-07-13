from sqlalchemy.ext.asyncio import AsyncSession

from planty.domain.entities import Task
from planty.infrastructure.repositories import SQLAlchemyTaskRepository


async def test_task_repo(session: AsyncSession, nonperiodic_task: Task) -> None:
    task_repo = SQLAlchemyTaskRepository(session)

    await task_repo.add(nonperiodic_task)
    await session.commit()

    task_got = await task_repo.get(nonperiodic_task.id)
    assert task_got
    assert task_got.id == nonperiodic_task.id
    assert task_got.user_id == nonperiodic_task.user_id
    assert task_got.title == nonperiodic_task.title
    assert task_got.description == nonperiodic_task.description
    assert task_got.is_completed == nonperiodic_task.is_completed
    assert task_got.added_at == nonperiodic_task.added_at
    assert task_got.due_to_next == nonperiodic_task.due_to_next
    assert task_got.due_to_days_period == nonperiodic_task.due_to_days_period


# TODO: test UserRepository
