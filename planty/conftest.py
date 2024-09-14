import os


# substitute the `MODE` _before_ the Settings object is created.
os.environ["MODE"] = "TEST"
import pytest  # noqa: E402

from planty.domain.entities import Section, Task, User, Username  # noqa: E402
from planty.utils import get_datetime_now, get_today  # noqa: E402
from planty.application.uow import IUnitOfWork, SqlAlchemyUnitOfWork  # noqa: E402


# these fixtures are shared across different test sets:


@pytest.fixture
def user() -> User:
    return User(username=Username("test_user"))


@pytest.fixture
def section() -> Section:
    return Section(title="Test section #1", tasks=[])


@pytest.fixture
def nonperiodic_task(user: User, section: Section) -> Task:
    return Task(
        user_id=user.id,
        title="Get some cheese",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=None,
        due_to_days_period=None,
        section_id=section.id,
    )


@pytest.fixture
def everyday_task(user: User, section: Section) -> Task:
    return Task(
        user_id=user.id,
        title="Read something interesting",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=1,
        section_id=section.id,
    )


@pytest.fixture
def every_three_days_task(user: User, section: Section) -> Task:
    return Task(
        user_id=user.id,
        title="Plant waters",
        description=None,
        is_completed=False,
        added_at=get_datetime_now(),
        due_to_next=get_today(),
        due_to_days_period=3,
        section_id=section.id,
    )
