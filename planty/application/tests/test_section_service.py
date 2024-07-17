from planty.application.services import SectionService
from planty.application.uow import IUnitOfWork
from planty.domain.entities import Section, Task


async def test_add_task_to_section(
    uow: IUnitOfWork,
    nonperiodic_task: Task,
    section: Section,
) -> None:
    section_service = SectionService(uow)
    task_repo, section_repo = uow.task_repo, uow.section_repo
    await section_repo.add(section)
    section_before = await section_service.get_section(section.id)
    assert section_before
    assert section_before.tasks == []
    await task_repo.add(nonperiodic_task)
    section_after = await section_service.get_section(section.id)
    assert section_after
    assert section_after.tasks == [nonperiodic_task]
