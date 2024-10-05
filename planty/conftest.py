import os

# substitute the `PLANTY_MODE` _before_ the Settings object is created.
os.environ["PLANTY_MODE"] = "TEST"
import json  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import pytest  # noqa: E402


# these fixtures are shared across different test sets:


# supports datetimes copied from dbeaver
TEST_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@pytest.fixture(scope="session")
def test_data() -> dict[str, list[dict[str, Any]]]:
    return _load_json_with_data("data.json")


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
                if column == "due_to" and row[column]:
                    row[column] = datetime.strptime(row[column], "%Y-%m-%d").date()

    # TODO: make this dict immutable to prevent accidental modification
    return test_data


@pytest.fixture(scope="session")
def users_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["users"]


@pytest.fixture(scope="session")
def tasks_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["tasks"]


@pytest.fixture(scope="session")
def sections_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["sections"]
