from typing import Optional
from contextlib import AbstractContextManager, nullcontext as does_not_raise
import pytest
from planty.domain.task import Section, Task
from planty.domain.exceptions import (
    MovingSectionIndexError,
    RemovingSectionFromWrongSectionError,
    RemovingTaskFromWrongSectionError,
    MovingTaskIndexError,
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
    nonempty_section: Section,
    nonperiodic_task: Task,
    index: Optional[int],
    expected_raises: Optional[AbstractContextManager[None]],
) -> None:
    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()
    section = nonempty_section
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
def test_remove_task_from_section(nonempty_section: Section, task_index: int) -> None:
    section = nonempty_section
    task = section.tasks[task_index]
    tasks = section.tasks.copy()

    section.remove_task(task)

    assert len(section.tasks) == len(tasks) - 1
    tasks.remove(task)
    assert section.tasks == tasks


def test_remove_task_from_wrong_section(
    nonempty_section: Section, nonperiodic_task: Task
) -> None:
    section = nonempty_section
    task = nonperiodic_task
    assert task.section_id != section.id

    with pytest.raises(RemovingTaskFromWrongSectionError):
        section.remove_task(task)


@pytest.mark.parametrize("task_index", [0, 1, 2, 3])
def test_move_task_to_the_same_section(
    nonempty_section: Section, task_index: int
) -> None:
    section = nonempty_section
    task = section.tasks[task_index]
    task_ids_before = {task.id for task in section.tasks}

    index_to_move = 2

    Section.move_task(task, section, section, index_to_move)

    task_ids = {task.id for task in section.tasks}
    assert task_ids_before == task_ids
    assert section.tasks[index_to_move] == task


@pytest.mark.parametrize(
    "index_from_move, index_to_move, mistakenly_swap, expected_raises",
    [
        (0, 0, False, None),
        (1, 0, False, None),
        (2, 0, False, None),
        (0, 1, False, None),
        (1, 1, False, None),
        (2, 1, False, None),
        (0, 2, False, None),
        (1, 2, False, None),
        (2, 2, False, None),
        (3, 2, False, None),
        (1, 327, False, pytest.raises(MovingTaskIndexError)),
        (1, 1, True, pytest.raises(RemovingTaskFromWrongSectionError)),
    ],
)
def test_move_task_to_the_another_section(
    nonempty_section: Section,
    section_current_tasks: Section,
    index_from_move: int,
    index_to_move: int,
    expected_raises: Optional[AbstractContextManager[None]],
    mistakenly_swap: bool,
) -> None:
    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()

    assert nonempty_section != section_current_tasks
    section_to = nonempty_section
    section_from = section_current_tasks

    task = (section_from if not mistakenly_swap else section_to).tasks[index_from_move]

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
    "index_from_move, index_to_move, mistakenly_swap, expected_raises",
    [
        (0, 0, False, None),
        (1, 0, False, None),
        (2, 0, False, None),
        (0, 1, False, None),
        (1, 1, False, None),
        (2, 1, False, None),
        (1, 327, False, pytest.raises(MovingSectionIndexError)),
        (1, 1, True, pytest.raises(RemovingSectionFromWrongSectionError)),
    ],
)
def test_move_section_to_another_section(
    section_sometimes_later: Section,
    section_current_tasks: Section,
    index_from_move: int,
    index_to_move: int,
    expected_raises: Optional[AbstractContextManager[None]],
    mistakenly_swap: bool,
) -> None:
    assert len(section_current_tasks.subsections) >= 2
    assert len(section_sometimes_later.subsections) >= 4

    raises_exception = bool(expected_raises)
    if not expected_raises:
        expected_raises = does_not_raise()

    assert section_sometimes_later != section_current_tasks

    section_from = section_sometimes_later
    section_to = section_current_tasks

    section = section_from.subsections[index_from_move]

    if mistakenly_swap:
        section_to, section_from = section_from, section_to

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


def test_shuffle_tasks(nonempty_section: Section) -> None:
    section = nonempty_section
    task_ids_before = {task.id for task in section.tasks}
    len_before = len(section.tasks)
    section.shuffle_tasks()
    task_ids_after = {task.id for task in section.tasks}
    len_after = len(section.tasks)
    assert task_ids_before == task_ids_after
    assert len_before == len_after
