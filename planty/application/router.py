from datetime import date
from uuid import UUID

from fastapi import APIRouter, status

from planty.application.schemas import (
    RequestAttachmentUpload,
    AttachmentUploadInfo,
    SectionCreateRequest,
    SectionCreateResponse,
    SectionResponse,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskMoveRequest,
    TaskRemoveRequest,
    TasksByDateResponse,
    TaskToggleCompletedRequest,
    TaskToggleCompletedResponse,
    TaskUpdateRequest,
    TaskUpdateResponse,
    SectionsListResponse,
)
from planty.application.services.tasks import (
    SectionService,
    TaskService,
)
from planty.application.uow import SqlAlchemyUnitOfWork

router = APIRouter(tags=["User tasks"], prefix="/api")


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreateRequest) -> TaskCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        task_id = await section_service.create_task(task_data)
        await uow.commit()
        return TaskCreateResponse(id=task_id)


# TODO: use query params for DELETE, body must be empty!
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
) -> TasksByDateResponse:
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


@router.post(
    "/task/attachment",
    description=(
        "This endpoint allows the frontend to obtain a pre-signed POST URL along "
        "with the required fields for uploading an attachment to an S3-compatible "
        "storage. The frontend is responsible for encrypting the file client-side "
        "using AES-128 CBC with the provided key and IV. After encryption, the frontend "
        "directly uploads the file to the S3 storage using the pre-signed URL and fields. "
        "\n\nThe frontend can include the 'Content-Disposition' header in the "
        "upload request to specify the file name, ensuring that the file is downloaded "
        "later with the correct name."
        "\n\nThe approach with client-side encryption allows using even non-trusted "
        "S3 Storage providers for user files."
    ),
)
async def get_attachment_uploading_info(
    request: RequestAttachmentUpload,
) -> AttachmentUploadInfo:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        upload_info = await task_service.add_attachment(request)
        await uow.commit()
    return upload_info


@router.delete("/task/{task_id}/attachment/{attachment_id}")
async def remove_attachment(task_id: UUID, attachment_id: UUID) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        await task_service.remove_attachment(task_id, attachment_id)
        await uow.commit()


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
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.get_section(section_id)
        return section


@router.get("/sections")
async def get_sections() -> SectionsListResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        sections = await section_service.get_all_sections()
        return sections


@router.post("/section/shuffle")
async def shuffle_section(
    request: ShuffleSectionRequest,
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.shuffle(request)
        await uow.commit()
        return section
