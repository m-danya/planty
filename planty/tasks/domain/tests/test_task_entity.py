from datetime import timedelta
import pytest
from planty.tasks.domain.entities import Task
from planty.utils import get_today, get_datetime_now


@pytest.fixture
def nonperiodic_task():
    return Task(
        id=1,
        user_id=1,
        section_id=1,
        title="Get some cheese",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=None,
        due_to_days_period=None,
    )


@pytest.fixture
def everyday_task():
    return Task(
        id=1,
        user_id=1,
        section_id=1,
        title="Read something interesting",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=1,
    )


@pytest.fixture
def every_three_days_task():
    return Task(
        id=1,
        user_id=1,
        section_id=1,
        title="Plant waters",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=3,
    )


def test_completion_nonperiodic(nonperiodic_task):
    assert not nonperiodic_task.is_completed
    nonperiodic_task.mark_completed()
    assert nonperiodic_task.is_completed


def test_completion_everyday(everyday_task):
    assert not everyday_task.is_completed
    assert everyday_task.due_to_next == get_today()
    everyday_task.mark_completed()
    assert not everyday_task.is_completed
    assert everyday_task.due_to_next == get_today() + timedelta(days=1)


def test_completion_every_three_days(every_three_days_task):
    task = every_three_days_task
    assert not task.is_completed
    assert task.due_to_next == get_today()
    task.mark_completed()
    assert not task.is_completed
    assert task.due_to_next == get_today() + timedelta(days=3)
