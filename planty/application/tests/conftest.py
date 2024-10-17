from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from planty.application.auth import current_user
from planty.config import settings
from planty.domain.task import User
from planty.infrastructure.database import Base, engine, raw_async_session_maker
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)
from planty.main import app as fastapi_app
import subprocess
import httpx
import asyncio


@pytest.fixture(scope="function", autouse=True)
async def prepare_database(test_data: dict[str, list[dict[str, Any]]]) -> None:
    assert settings.mode == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with raw_async_session_maker() as session:
        for Model, table_key in [
            (UserModel, "users"),
            (SectionModel, "sections"),
            (TaskModel, "tasks"),
            (AttachmentModel, "attachments"),
        ]:
            for item in test_data[table_key]:
                session.add(Model(**item))

        await session.commit()


@pytest.fixture(scope="function")
async def ac(test_user: User) -> AsyncGenerator[AsyncClient, None]:
    # Mock `current_user` with `test_user`:
    fastapi_app.dependency_overrides[current_user] = lambda: test_user
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),  # type: ignore
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def minio_container() -> AsyncGenerator[None, None]:
    minio_was_started_in_test = False
    try:
        result = subprocess.run(
            "docker compose ps -q minio", shell=True, capture_output=True, text=True
        )
        if not result.stdout.strip():
            subprocess.run(
                "docker compose up -d minio minio-createbuckets",
                shell=True,
                check=True,
            )
            minio_was_started_in_test = True

        async with httpx.AsyncClient() as client:
            for _ in range(10):
                try:
                    response = await client.get(
                        f"{settings.aws_url}/minio/health/ready", timeout=1
                    )
                    if response.status_code == 200:
                        break
                except httpx.RequestError:
                    pass
                await asyncio.sleep(1)
            else:
                raise TimeoutError("MinIO container did not become ready in time.")

        yield
    finally:
        if minio_was_started_in_test and settings.shutdown_containers_after_test:
            subprocess.run(
                "docker compose down",
                shell=True,
                check=True,
            )
