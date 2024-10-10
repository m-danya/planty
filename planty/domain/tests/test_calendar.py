from datetime import date


import pytest

from planty.domain.calendar import (
    get_task_recurrences,
    multiply_tasks_with_recurrences,
    recurrence_rule,
)
from planty.domain.task import Task
from planty.domain.types import RecurrencePeriodType


@pytest.mark.parametrize(
    "start_day,k,period_type,not_after,result",
    [
        (
            date(2024, 8, 31),
            1,
            "months",
            date(2025, 1, 1),
            [
                date(2024, 8, 31),
                date(2024, 9, 30),
                date(2024, 10, 31),
                date(2024, 11, 30),
                date(2024, 12, 31),
            ],
        ),
        (
            date(2024, 8, 31),
            1,
            "days",
            date(2024, 8, 31),
            [date(2024, 8, 31)],
        ),
        (
            date(2024, 8, 31),
            1,
            "days",
            date(2024, 9, 2),
            [date(2024, 8, 31), date(2024, 9, 1), date(2024, 9, 2)],
        ),
        (
            date(2024, 8, 31),
            3,
            "months",
            date(2025, 9, 2),
            [
                date(2024, 8, 31),
                date(2024, 11, 30),
                date(2025, 2, 28),
                date(2025, 5, 31),
                date(2025, 8, 31),
            ],
        ),
    ],
)
def test_recurrence_rule(
    start_day: date,
    k: int,
    period_type: RecurrencePeriodType,
    not_after: date,
    result: list[date],
) -> None:
    dates = list(
        recurrence_rule(
            start_day=start_day,
            k=k,
            period_type=period_type,
            not_after=not_after,
        )
    )
    assert dates == result


@pytest.mark.parametrize(
    "not_after, expected_dates",
    [
        (date(1997, 12, 31), []),
        (date(2001, 1, 1), [date(2001, 1, 1)]),
        (date(2001, 1, 2), [date(2001, 1, 1)]),
        (date(2001, 1, 4), [date(2001, 1, 1), date(2001, 1, 4)]),
        (
            date(2001, 1, 10),
            [date(2001, 1, 1), date(2001, 1, 4), date(2001, 1, 7), date(2001, 1, 10)],
        ),
    ],
)
def test_get_task_recurrences(
    task_from_2001: Task, not_after: date, expected_dates: list[date]
) -> None:
    recurrences = get_task_recurrences(task_from_2001, not_after)
    assert recurrences == expected_dates


def test_get_task_recurrences_with_nonperiodic(nonperiodic_task: Task) -> None:
    recurrences = get_task_recurrences(nonperiodic_task, date(2001, 1, 1))
    assert recurrences == []


@pytest.mark.parametrize(
    "not_after",
    [
        date(1997, 12, 31),
        date(2001, 1, 1),
        date(2001, 1, 2),
        date(2099, 1, 4),
        date(2099, 1, 10),
    ],
)
def test_get_task_recurrence_with_no_recurrence(
    task_with_due_to_and_no_recurrence: Task, not_after: date
) -> None:
    task = task_with_due_to_and_no_recurrence
    assert task.due_to is not None
    recurrences = get_task_recurrences(task, not_after)
    if not_after >= task.due_to:
        assert recurrences == [task.due_to]
    else:
        assert recurrences == []


def test_multiply_tasks_with_recurrences(
    task_from_2001: Task,
) -> None:
    not_after = date(2002, 12, 31)
    expected_len = 244
    tasks_by_date = multiply_tasks_with_recurrences([task_from_2001], not_after)
    assert sum(len(tasks_by_date[date_]) for date_ in tasks_by_date) == expected_len
