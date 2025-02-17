from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from planty.application.auth import admin_user, current_user
from planty.application.schemas import (
    ArchivedTasksResponse,
    AttachmentUploadInfo,
    RequestAttachmentUpload,
    SectionCreateRequest,
    SectionCreateResponse,
    SectionMoveRequest,
    SectionResponse,
    SectionsListResponse,
    SectionUpdateRequest,
    SectionUpdateResponse,
    ShuffleSectionRequest,
    StatsResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskMoveRequest,
    TaskRemoveRequest,
    TasksByDatesResponse,
    TaskSearchResponse,
    TaskToggleArchivedRequest,
    TaskToggleCompletedRequest,
    TaskUpdateRequest,
    TaskUpdateResponse,
)
from planty.application.services.admin import AdminService
from planty.application.services.tasks import (
    SectionService,
    TaskService,
)
from planty.application.uow import SqlAlchemyUnitOfWork
from planty.domain.task import User

router = APIRouter(tags=["User tasks"], prefix="/api")

templates = Jinja2Templates(directory="planty/application/templates")


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest, user: User = Depends(current_user)
) -> TaskCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        task_id = await section_service.create_task(user.id, task_data)
        await uow.commit()
        return TaskCreateResponse(id=task_id)


# TODO: use query params for DELETE, body must be empty!
@router.delete("/task")
async def remove_task(
    task_data: TaskRemoveRequest, user: User = Depends(current_user)
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        await section_service.remove_task(user.id, task_data.task_id)
        await uow.commit()


@router.patch("/task")
async def update_task(
    task_data: TaskUpdateRequest, user: User = Depends(current_user)
) -> TaskUpdateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        task = await task_service.update_task(user.id, task_data)
        await uow.commit()
        return TaskUpdateResponse(task=task)


@router.get("/task/by_date")
async def get_tasks_by_date(
    not_before: date,
    not_after: date,
    user: User = Depends(current_user),
    with_overdue: bool = False,
) -> TasksByDatesResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        tasks_by_date = await task_service.get_tasks_by_date(
            user.id, not_before, not_after, with_overdue
        )
        await uow.commit()
        return tasks_by_date


@router.get("/task/search")
async def get_tasks_by_search_query(
    query: str, user: User = Depends(current_user)
) -> TaskSearchResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        tasks = await task_service.get_tasks_by_search_query(user.id, query)
        return tasks


@router.post("/task/move")
async def move_task(
    request: TaskMoveRequest, user: User = Depends(current_user)
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        await section_service.move_task(user.id, request)
        await uow.commit()


# TODO: make this endpoint idempotent
@router.post("/task/toggle_completed")
async def toggle_task_completed(
    request: TaskToggleCompletedRequest, user: User = Depends(current_user)
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.toggle_task_completed(
            user.id,
            request.task_id,
            auto_archive=request.auto_archive,  # TODO: move `auto_archive` to user settings?
        )
        await uow.commit()
    return section


# TODO: make this endpoint idempotent
@router.post("/task/toggle_archived")
async def toggle_task_archived(
    request: TaskToggleArchivedRequest, user: User = Depends(current_user)
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.toggle_task_archived(
            user.id,
            request.task_id,
        )
        await uow.commit()
    return section


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
    request: RequestAttachmentUpload, user: User = Depends(current_user)
) -> AttachmentUploadInfo:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        upload_info = await task_service.add_attachment(user.id, request)
        await uow.commit()
    return upload_info


@router.delete("/task/{task_id}/attachment/{attachment_id}")
async def remove_attachment(
    task_id: UUID, attachment_id: UUID, user: User = Depends(current_user)
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        await task_service.remove_attachment(user.id, task_id, attachment_id)
        await uow.commit()


@router.get("/tasks/archived")
async def get_archived_tasks(
    user: User = Depends(current_user),
) -> ArchivedTasksResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        task_service = TaskService(uow=uow)
        return await task_service.get_archived_tasks(user.id)


@router.post("/section", status_code=status.HTTP_201_CREATED)
async def create_section(
    section_data: SectionCreateRequest, user: User = Depends(current_user)
) -> SectionCreateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.add(user.id, section_data)
        await uow.commit()
        return SectionCreateResponse(id=section.id)


@router.get("/section/{section_id}")
async def get_section(
    section_id: UUID, user: User = Depends(current_user)
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.get_section(user.id, section_id)
        return section


@router.patch("/section")
async def patch_section(
    section_data: SectionUpdateRequest, user: User = Depends(current_user)
) -> SectionUpdateResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.update_section(user.id, section_data)
        await uow.commit()
        return SectionUpdateResponse(section=section)


@router.post("/section/move")
async def move_section(
    request: SectionMoveRequest, user: User = Depends(current_user)
) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        await section_service.move_section(user.id, request)
        await uow.commit()


@router.get("/sections")
async def get_sections(
    user: User = Depends(current_user),
    leaves_only: bool = False,
    as_tree: bool = True,
) -> SectionsListResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        sections = await section_service.get_all_sections(
            user.id, leaves_only=leaves_only, as_tree=as_tree
        )
        return sections


@router.post("/section/shuffle")
async def shuffle_section(
    request: ShuffleSectionRequest, user: User = Depends(current_user)
) -> SectionResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        section_service = SectionService(uow=uow)
        section = await section_service.shuffle(user.id, request)
        await uow.commit()
        return section


# ADMIN STATS & CONTROLS
# TODO: rework and move to separate router


@router.get("/user/stats")
async def get_stats(admin_user: User = Depends(admin_user)) -> StatsResponse:
    async with SqlAlchemyUnitOfWork() as uow:
        admin_service = AdminService(uow=uow)
        return await admin_service.get_stats()


@router.get("/user/verify", response_class=HTMLResponse)
async def verify_user_form(
    request: Request, admin: User = Depends(admin_user)
) -> HTMLResponse:
    return templates.TemplateResponse("verify_user.html", {"request": request})


@router.post("/user/{user_id}/verify")
async def verify_user(user_id: UUID, admin: User = Depends(admin_user)) -> None:
    async with SqlAlchemyUnitOfWork() as uow:
        admin_service = AdminService(uow=uow)
        await admin_service.verify_user(user_id)
        await uow.commit()
