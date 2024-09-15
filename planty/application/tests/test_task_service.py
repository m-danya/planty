from planty.application.schemas import TaskCreateRequest
from planty.application.services import TaskService
from planty.application.uow import SqlAlchemyUnitOfWork
from planty.domain.entities import Section, Task, User


async def test_add_task(
    nonperiodic_task: Task,
    persisted_user: User,
    persisted_section: Section,
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        task_repo = uow.task_repo
        task_service = TaskService(uow)

        task, user, section = nonperiodic_task, persisted_user, persisted_section

        task.section_id = section.id
        task.user_id = user.id

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
    persisted_user: User,
    persisted_section: Section,
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow)

        task, user, section = nonperiodic_task, persisted_user, persisted_section

        task.section_id = section.id
        task.user_id = user.id

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
