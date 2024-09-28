from datetime import date
from uuid import UUID

from fastapi import APIRouter, status

from planty.application.schemas import (
    SectionCreateRequest,
    SectionCreateResponse,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskMoveRequest,
    TaskRemoveRequest,
    TaskToggleCompletedRequest,
    TaskToggleCompletedResponse,
    TaskUpdateRequest,
    TaskUpdateResponse,
)
from planty.application.services import SectionService, TaskService
from planty.application.uow import SqlAlchemyUnitOfWork
from planty.domain.task import Section, Task

router = APIRouter(tags=["User tasks"], prefix="/api")


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreateRequest) -> TaskCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        task_id = await section_service.create_task(task_data)
        await uow.commit()
        return TaskCreateResponse(id=task_id)


@router.delete("/task")
async def remove_task(task_data: TaskRemoveRequest) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        await section_service.remove_task(task_data.task_id)
        await uow.commit()


@router.patch("/task")
async def update_task(task_data: TaskUpdateRequest) -> TaskUpdateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        task = await task_service.update_task(task_data)
        await uow.commit()
        return TaskUpdateResponse(task=task)


@router.get("/task/by_date")
async def get_tasks_by_date(
    user_id: UUID,
    not_before: date,
    not_after: date,
) -> dict[date, list[Task]]:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        tasks_by_date = await task_service.get_tasks_by_date(
            user_id, not_before, not_after
        )
        await uow.commit()
        return tasks_by_date


@router.post("/task/move")
async def move_task(request: TaskMoveRequest) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        await section_service.move_task(request)
        await uow.commit()


@router.post("/task/toggle_completed")
async def toggle_task_completed(
    request: TaskToggleCompletedRequest,
) -> TaskToggleCompletedResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        is_completed = await task_service.toggle_task_completed(request.task_id)
        await uow.commit()
    return TaskToggleCompletedResponse(is_completed=is_completed)


@router.post("/section", status_code=status.HTTP_201_CREATED)
async def create_section(
    section_data: SectionCreateRequest,
) -> SectionCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.add(section_data)
        await uow.commit()
        return SectionCreateResponse(id=section.id)


@router.get("/section/{section_id}")
async def get_section(
    section_id: UUID,
) -> Section:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.get_section(section_id)
        return section


@router.get("/sections")
async def get_sections() -> list[Section]:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        sections = await section_service.get_all_sections()
        return sections


@router.post("/section/shuffle")
async def shuffle_section(
    request: ShuffleSectionRequest,
) -> Section:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.shuffle(request)
        await uow.commit()
        return section
