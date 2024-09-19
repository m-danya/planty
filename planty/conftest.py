import os

# substitute the `MODE` _before_ the Settings object is created.
os.environ["MODE"] = "TEST"
import json  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import pytest  # noqa: E402

from planty.application.uow import SqlAlchemyUnitOfWork  # noqa: E402
from planty.domain.entities import Section, Task, User, Username  # noqa: E402
from planty.utils import get_datetime_now, get_today  # noqa: E402

# these fixtures are shared across different test sets:


# supports datetimes copied from dbeaver
TEST_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@pytest.fixture(scope="session")
def db_test_data() -> dict[str, list[dict[str, Any]]]:
    return _load_json_with_data("db_data.json")


@pytest.fixture(scope="session")
def additional_test_data() -> dict[str, Any]:
    return _load_json_with_data("additional_data.json")


def _load_json_with_data(filename: str) -> dict[str, Any]:
    with open(Path(__file__).parent / "resources" / filename) as f:
        test_data: dict[str, Any] = json.load(f)
    for table_key in test_data:
        for row in test_data[table_key]:
            for column in row:
                if row[column] is None:
                    continue
                if column.endswith("_at"):
                    row[column] = datetime.strptime(row[column], TEST_DATETIME_FORMAT)
                if column == "due_to_next" and row[column]:
                    row[column] = datetime.strptime(row[column], "%Y-%m-%d").date()
    test_data["users"].sort(key=lambda x: x.get("id"))
    test_data["sections"].sort(key=lambda x: x.get("id"))
    test_data["tasks"].sort(key=lambda x: x.get("id"))
    # TODO: make this dict immutable to prevent accidental modification
    return test_data


@pytest.fixture(scope="session")
def db_tasks_data(
    db_test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return db_test_data["tasks"]


@pytest.fixture(scope="session")
def db_sections_data(
    db_test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return db_test_data["sections"]


@pytest.fixture
def user() -> User:
    return User(username=Username("test_user_2"))


@pytest.fixture
def section() -> Section:
    return Section(title="Test section #1", tasks=[])


@pytest.fixture
async def persisted_user(user: User) -> User:
    async with SqlAlchemyUnitOfWork() as uow:
        await uow.user_repo.add(user)
        await uow.commit()
    return user


@pytest.fixture
async def persisted_section(section: Section) -> Section:
    async with SqlAlchemyUnitOfWork() as uow:
        await uow.section_repo.add(section)
        await uow.commit()
    return section


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
