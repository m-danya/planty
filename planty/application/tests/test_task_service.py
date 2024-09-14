from planty.application.schemas import TaskCreateRequest
from planty.application.services import TaskService
from planty.application.uow import IUnitOfWork, SqlAlchemyUnitOfWork
from planty.domain.entities import Section, Task, User


async def test_add_task(
    nonperiodic_task: Task,
    user: User,
    section: Section,
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        user_repo = uow.user_repo
        task_repo = uow.task_repo
        task_service = TaskService(uow)
        await user_repo.add(user)
        task = nonperiodic_task
        task_create_request = TaskCreateRequest(
            user_id=user.id,
            section_id=section.id,
            title=task.title,
            description=task.description,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )

        task_id = await task_service.add_task(task_create_request)
        task_got = await task_repo.get(task_id)
        assert task_got
        assert task_got.id == task_id
        assert task_got.title == task.title


async def test_mark_completed_task(
    nonperiodic_task: Task,
    user: User,
    section: Section,
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        user_repo = uow.user_repo
        task_service = TaskService(uow)
        await user_repo.add(user)
        task = nonperiodic_task
        task_create_request = TaskCreateRequest(
            user_id=user.id,
            section_id=section.id,
            title=task.title,
            description=task.description,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )

        task_id = await task_service.add_task(task_create_request)

        task_before: Task = await task_service.get_task(task_id)
        assert task_before.is_completed is False
        await task_service.mark_task_completed(task_id)
        task_after: Task = await task_service.get_task(task_id)
        assert task_after.is_completed is True
