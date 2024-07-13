
from planty.application.services import SectionService
from planty.domain.entities import Section, Task
from planty.infrastructure.repositories import (
    ISectionRepository,
    ITaskRepository,
)


async def test_add_task_to_section(
    section_repo: ISectionRepository,
    task_repo: ITaskRepository,
    nonperiodic_task: Task,
    section: Section,
    section_service: SectionService,
) -> None:
    await section_repo.add(section)
    section_before = await section_service.get_section(section.id)
    assert section_before
    assert section_before.tasks == []
    await task_repo.add(nonperiodic_task)
    section_after = await section_service.get_section(section.id)
    assert section_after
    assert section_after.tasks == [nonperiodic_task]
