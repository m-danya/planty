import asyncio
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import func, select

from planty.config import settings
from planty.infrastructure.database import raw_async_session_maker
from planty.infrastructure.models import SectionModel, TaskModel, UserModel

SEED_DATA_PATH = Path(__file__).parents[1] / "resources" / "data.json"


def _load_seed_data() -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = json.loads(SEED_DATA_PATH.read_text())

    for items in data.values():
        for item in items:
            for key, value in item.items():
                if value is None:
                    continue
                if key == "id" or key.endswith("_id"):
                    item[key] = UUID(value)
                elif key == "added_at":
                    item[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                elif key == "due_to":
                    item[key] = date.fromisoformat(value)

    return data


async def seed_database() -> None:
    if settings.mode != "DEV":
        raise RuntimeError("Development data can only be loaded in PLANTY_MODE=DEV")

    data = _load_seed_data()
    async with raw_async_session_maker() as session:
        counts = [
            await session.scalar(select(func.count()).select_from(model))
            for model in (UserModel, SectionModel, TaskModel)
        ]
        if any(counts):
            raise RuntimeError(
                "Database is not empty. Remove planty.db, run migrations, and retry."
            )

        for model, key in (
            (UserModel, "users"),
            (SectionModel, "sections"),
            (TaskModel, "tasks"),
        ):
            session.add_all(model(**item) for item in data[key])

        await session.commit()

    print(
        "Loaded development data: "
        f"{len(data['users'])} users, "
        f"{len(data['sections'])} sections, "
        f"{len(data['tasks'])} tasks."
    )
    print("Login: user@example.ru / user@example.ru")


if __name__ == "__main__":
    asyncio.run(seed_database())
