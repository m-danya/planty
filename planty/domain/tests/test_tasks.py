from datetime import date, timedelta

import pytest

from planty.domain.task import Task
from planty.utils import get_today
from planty.domain.types import RecurrencePeriodType



def test_toggle_completed_nonperiodic(nonperiodic_task: Task) -> None:
    task = nonperiodic_task
    assert not task.is_completed
    assert not task.is_archived

    task.toggle_completed()
    assert task.is_completed
    assert task.is_archived

    task.toggle_completed()
    assert not task.is_completed
    assert not task.is_archived


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
    assert task.recurrence
    task.recurrence.flexible_mode = is_enabled
    assert task.recurrence
    assert task.due_to
    if is_enabled:
        expected_due_to = get_today() + timedelta(days=task.recurrence.period)
    else:
        expected_due_to = task.due_to + timedelta(days=task.recurrence.period)

    task.mark_completed()

    assert task.due_to == expected_due_to


@pytest.mark.parametrize(
    "start_day, period, period_type, expected_next_date",
    [
        (
            date(2024, 8, 31),
            1,
            "months",
            date(2024, 9, 30),
        ),
        (
            date(2024, 8, 31),
            1,
            "days",
            date(2024, 9, 1),
        ),
        (
            date(2024, 1, 31),
            1,
            "months",
            date(2024, 2, 29),
        ),
        (
            date(2024, 1, 15),
            2,
            "months",
            date(2024, 3, 15),
        ),
        (
            date(2023, 3, 1),
            1,
            "years",
            date(2024, 3, 1),
        ),
    ],
)
def test_recurrent_task_completion(
    task_from_2001: Task,
    start_day: date,
    period: int,
    period_type: RecurrencePeriodType,
    expected_next_date: date,
) -> None:
    task = task_from_2001
    task.due_to = start_day
    assert task.recurrence
    task.recurrence.period = period
    task.recurrence.type = period_type
    task.recurrence.flexible_mode = False

    task.mark_completed()

    assert not task.is_completed
    assert task.due_to == expected_next_date
