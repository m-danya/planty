from planty.application.services import SectionService
from planty.application.uow import SqlAlchemyUnitOfWork
from planty.domain.entities import Section, Task, User


async def test_add_task_to_section(
    persisted_user: User,
    nonperiodic_task: Task,
    persisted_section: Section,
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow)

        task, section, user = nonperiodic_task, persisted_section, persisted_user
        task.section_id = section.id
        task.user_id = user.id

        section_before = await section_service.get_section(section.id)
        assert section_before
        assert section_before.tasks == []

        await uow.task_repo.add(nonperiodic_task)
        section_after = await section_service.get_section(section.id)
        assert section_after
        assert section_after.tasks == [nonperiodic_task]
