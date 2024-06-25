from datetime import timedelta

from planty.domain.entities import Task
from planty.utils import get_today


def test_completion_nonperiodic(nonperiodic_task: Task) -> None:
    assert not nonperiodic_task.is_completed
    nonperiodic_task.mark_completed()
    assert nonperiodic_task.is_completed


def test_completion_everyday(everyday_task: Task) -> None:
    assert not everyday_task.is_completed
    assert everyday_task.due_to_next == get_today()
    everyday_task.mark_completed()
    assert not everyday_task.is_completed
    assert everyday_task.due_to_next == get_today() + timedelta(days=1)


def test_completion_every_three_days(every_three_days_task: Task) -> None:
    task = every_three_days_task
    assert not task.is_completed
    assert task.due_to_next == get_today()
    task.mark_completed()
    assert not task.is_completed
    assert task.due_to_next == get_today() + timedelta(days=3)
