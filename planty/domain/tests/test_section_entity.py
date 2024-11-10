from typing import Optional
from contextlib import AbstractContextManager, nullcontext as does_not_raise
from uuid import UUID
import pytest
from planty.conftest import find_entity_by_id
from planty.domain.task import Section, Task
from planty.domain.exceptions import (
    MisplaceSectionIndexError,
    RemovingSectionFromWrongSectionError,
    RemovingTaskFromWrongSectionError,
    MovingTaskIndexError,
    SectionCantBothHaveTasksAndSubsection,
)


@pytest.mark.parametrize(
    "index, expected_raises",
    [
        (None, None),
        (0, None),
        (1, None),
        (2, None),
        (3, None),
        (327, pytest.raises(MovingTaskIndexError)),
    ],
)
def test_insert_task_in_section(
    chores_section: Section,
    nonperiodic_task: Task,
    index: Optional[int],
    expected_raises: Optional[AbstractContextManager[None]],
) -> None:
    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()
    section = chores_section
    task = nonperiodic_task
    assert task.section_id != section
    tasks = section.tasks.copy()

    with expected_raises:
        section.insert_task(task, index=index)

    if raises_exception:
        return
    if index is None:
        index = len(tasks)
    tasks.insert(index, task)
    assert section.tasks == tasks


@pytest.mark.parametrize("task_index", [0, 1, 2, 3])
def test_remove_task_from_section(chores_section: Section, task_index: int) -> None:
    section = chores_section
    task = section.tasks[task_index]
    tasks = section.tasks.copy()

    section.remove_task(task)

    assert len(section.tasks) == len(tasks) - 1
    tasks.remove(task)
    assert section.tasks == tasks


def test_remove_task_from_wrong_section(
    chores_section: Section, nonperiodic_task: Task
) -> None:
    section = chores_section
    task = nonperiodic_task
    assert task.section_id != section.id

    with pytest.raises(RemovingTaskFromWrongSectionError):
        section.remove_task(task)


@pytest.mark.parametrize("task_index", [0, 1, 2, 3])
def test_move_task_to_the_same_section(
    chores_section: Section, task_index: int
) -> None:
    section = chores_section
    task = section.tasks[task_index]
    task_ids_before = {task.id for task in section.tasks}

    index_to_move = 2

    Section.move_task(task, section, section, index_to_move)

    task_ids = {task.id for task in section.tasks}
    assert task_ids_before == task_ids
    assert section.tasks[index_to_move] == task


@pytest.mark.parametrize(
    "section_from_id, section_to_id, index_from_move, index_to_move, expected_raises",
    [
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            0,
            0,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            1,
            0,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            2,
            0,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            0,
            1,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            1,
            1,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            2,
            1,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            0,
            2,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            1,
            2,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            2,
            2,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            3,
            2,
            None,
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            1,
            327,
            pytest.raises(MovingTaskIndexError),
        ),
        (
            UUID("a5b2010d-c27c-4f22-be47-828e065f9607"),
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            -1,
            1,
            pytest.raises(RemovingTaskFromWrongSectionError),
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),  # has subsections
            3,
            0,
            pytest.raises(SectionCantBothHaveTasksAndSubsection),
        ),
        (
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),
            UUID(
                "0d966845-254b-4b5c-b8a7-8d34dcd3d527"
            ),  # root section, also has subsections
            3,
            0,
            pytest.raises(SectionCantBothHaveTasksAndSubsection),
        ),
    ],
)
def test_move_task_to_the_another_section(
    section_from_id: UUID,
    section_to_id: UUID,
    index_from_move: int,
    index_to_move: int,
    expected_raises: Optional[AbstractContextManager[None]],
    all_sections: list[Section],
) -> None:
    section_from = find_entity_by_id(all_sections, section_from_id)
    section_to = find_entity_by_id(all_sections, section_to_id)

    assert len(section_to.tasks) < 327
    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()

    if index_from_move == -1:
        # special case: take task from another section
        task = section_to.tasks[0]
    else:
        task = section_from.tasks[index_from_move]

    section_to_task_ids_before = {task.id for task in section_to.tasks}
    section_from_task_ids_before = {task.id for task in section_from.tasks}

    with expected_raises:
        Section.move_task(task, section_from, section_to, index_to_move)

    if raises_exception:
        return

    section_to_task_ids_after = {task.id for task in section_to.tasks}
    section_from_task_ids_after = {task.id for task in section_from.tasks}

    assert section_to_task_ids_before | {task.id} == section_to_task_ids_after
    assert section_from_task_ids_before - {task.id} == section_from_task_ids_after

    assert section_to.tasks[index_to_move] == task


@pytest.mark.parametrize(
    "section_from_id, section_to_id, index_from_move, index_to_move, expected_raises",
    [
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            0,
            0,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            1,
            0,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            2,
            0,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            0,
            1,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            1,
            1,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            2,
            1,
            None,
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            1,
            327,
            pytest.raises(MisplaceSectionIndexError),
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"),
            -1,
            1,
            pytest.raises(RemovingSectionFromWrongSectionError),
        ),
        (
            UUID("36ea0a4f-0334-464d-8066-aa359ecfdcba"),
            UUID("090eda97-dd2d-45bb-baa0-7814313e5a38"),  # has tasks
            1,
            0,
            pytest.raises(SectionCantBothHaveTasksAndSubsection),
        ),
    ],
)
def test_move_section_to_another_section(
    section_from_id: UUID,
    section_to_id: UUID,
    index_from_move: int,
    index_to_move: int,
    expected_raises: Optional[AbstractContextManager[None]],
    all_sections: list[Section],
) -> None:
    section_from = find_entity_by_id(all_sections, section_from_id)
    section_to = find_entity_by_id(all_sections, section_to_id)

    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()
    if index_from_move == -1:
        # special case: take any subsection from wrong section
        section = section_to.subsections[0]
    else:
        section = section_from.subsections[index_from_move]

    section_to_subsections_ids_before = {s.id for s in section_to.subsections}
    section_from_subsections_ids_before = {s.id for s in section_from.subsections}

    with expected_raises:
        Section.move_section(section, section_from, section_to, index_to_move)

    if raises_exception:
        return

    section_to_subsections_ids_after = {s.id for s in section_to.subsections}
    section_from_subsections_ids_after = {s.id for s in section_from.subsections}

    assert (
        section_to_subsections_ids_before | {section.id}
        == section_to_subsections_ids_after
    )
    assert (
        section_from_subsections_ids_before - {section.id}
        == section_from_subsections_ids_after
    )

    assert section_to.subsections[index_to_move] == section


def test_shuffle_tasks(chores_section: Section) -> None:
    section = chores_section
    task_ids_before = {task.id for task in section.tasks}
    len_before = len(section.tasks)
    section.shuffle_tasks()
    task_ids_after = {task.id for task in section.tasks}
    len_after = len(section.tasks)
    assert task_ids_before == task_ids_after
    assert len_before == len_after
