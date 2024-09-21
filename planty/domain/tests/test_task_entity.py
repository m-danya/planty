from datetime import timedelta

import pytest

from planty.domain.entities import Task
from planty.utils import get_today


def test_completion_nonperiodic(nonperiodic_task: Task) -> None:
    assert not nonperiodic_task.is_completed
    nonperiodic_task.mark_completed()
    assert nonperiodic_task.is_completed


def test_completion_everyday(everyday_task: Task) -> None:
    assert not everyday_task.is_completed
    everyday_task.due_to = get_today()
    everyday_task.mark_completed()
    assert not everyday_task.is_completed
    assert everyday_task.due_to == get_today() + timedelta(days=1)


@pytest.mark.parametrize(
    "is_enabled",
    [True, False],
)
def test_complete_flexible_recurrence(
    flexible_recurrence_task: Task, is_enabled: bool
) -> None:
    task = flexible_recurrence_task
    task.flexible_recurrence_mode = is_enabled
    if is_enabled:
        expected_due_to = get_today() + timedelta(days=task.recurrence_period)
    else:
        expected_due_to = task.due_to + timedelta(days=task.recurrence_period)

    task.mark_completed()

    assert task.due_to == expected_due_to
