from typing import Any
from uuid import UUID

from fastapi import APIRouter

from planty.application.schemas import (
    SectionCreateRequest,
    TaskCreateRequest,
)
from planty.application.services import SectionService, TaskService
from planty.application.uow import SqlAlchemyUnitOfWork

router = APIRouter(
    tags=["User tasks"],
)


# TODO: check username = "ab", does the validation work?


@router.post("/task")
async def create_task(
    task_data: TaskCreateRequest,
) -> Any:  # TODO: add validation
    task_service = TaskService(uow=SqlAlchemyUnitOfWork())
    await task_service.add_task(task_data)
    return {"message": "Task created"}


@router.post("/section")
async def create_section(
    section_data: SectionCreateRequest,
) -> Any:  # TODO: add validation
    section_service = SectionService(uow=SqlAlchemyUnitOfWork())
    section = await section_service.add(section_data)
    return {"message": "Session created", "id": section.id}


@router.get("/section/{section_id}")
async def get_section(
    section_id: UUID,
) -> Any:  # TODO: add validation
    section_service = SectionService(uow=SqlAlchemyUnitOfWork())
    section = await section_service.get_section(section_id)
    return section
