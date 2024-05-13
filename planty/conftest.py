import os

import pytest

from planty.domain.entities import Task, User
from planty.utils import get_datetime_now, get_today

# this file is located in the root of `planty` package to substitute the
# `MODE` environmental variable _before_ the Settings object is created.
os.environ["MODE"] = "TEST"

# these fixtures are shared across different test sets


@pytest.fixture
def user() -> User:
    return User(username="test_user")


@pytest.fixture
def nonperiodic_task(user) -> Task:
    return Task(
        user=user,
        title="Get some cheese",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=None,
        due_to_days_period=None,
    )


@pytest.fixture
def everyday_task(user) -> Task:
    return Task(
        user=user,
        title="Read something interesting",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=1,
    )


@pytest.fixture
def every_three_days_task(user) -> Task:
    return Task(
        user=user,
        title="Plant waters",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=3,
    )
