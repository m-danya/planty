from uuid import UUID

from fastapi import APIRouter

from planty.application.schemas import (
    SectionCreateRequest,
    SectionCreateResponse,
    ShuffleSectionRequest,
    ShuffleSectionResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskUpdateRequest,
    TaskUpdateResponse,
)
from planty.application.services import SectionService, TaskService
from planty.application.uow import SqlAlchemyUnitOfWork
from planty.domain.entities import Section

router = APIRouter(tags=["User tasks"], prefix="/api")


@router.post("/task")
async def create_task(
    task_data: TaskCreateRequest,
) -> TaskCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        task_id = await section_service.create_task(task_data)
        await uow.commit()
        return TaskCreateResponse(message="Task created", id=task_id)


@router.patch("/task")
async def update_task(
    task_data: TaskUpdateRequest,
) -> TaskUpdateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        task = await task_service.update_task(task_data)
        await uow.commit()
        return TaskUpdateResponse(message="Task updated", task=task)


@router.post("/section")
async def create_section(
    section_data: SectionCreateRequest,
) -> SectionCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.add(section_data)
        await uow.commit()
        return SectionCreateResponse(message="Session created", id=section.id)


@router.get("/section/{section_id}")
async def get_section(
    section_id: UUID,
) -> Section:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.get_section(section_id)
        return section


@router.get("/sections")
async def get_sections() -> list[Section]:  # TODO: move typing to schema
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        sections = await section_service.get_all_sections()
        return sections


@router.post("/section/shuffle")
async def shuffle_section(
    request: ShuffleSectionRequest,
) -> ShuffleSectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.shuffle(request)
        await uow.commit()
        return ShuffleSectionResponse(message="🎩 Done! 🪄", section=section)
