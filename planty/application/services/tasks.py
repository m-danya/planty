from datetime import date
from uuid import UUID

from planty.application.exceptions import (
    ForbiddenException,
    IncorrectDateInterval,
    TaskNotFoundException,
)
from planty.application.schemas import (
    ArchivedTasks,
    ArchivedTasksResponse,
    SectionCreateRequest,
    SectionMoveRequest,
    SectionResponse,
    SectionUpdateRequest,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskMoveRequest,
    TaskResponse,
    TasksByDatesResponse,
    TaskUpdateRequest,
    TaskSearchResponse,
    SectionsListResponse,
)
from planty.application.services.responses_converter import (
    convert_to_response,
)
from planty.application.uow import IUnitOfWork
from planty.domain.calendar import divide_tasks_by_dates
from planty.domain.exceptions import (
    ChangingRootSectionError,
    MisplaceSectionHierarchyError,
    SectionNotEmptyError,
    TaskCantBeOwnParentError,
    TaskHasSubtasksError,
)
from planty.domain.task import Section, Task


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self._task_repo = uow.task_repo
        self._user_repo = uow.user_repo

    async def update_task(
        self, user_id: UUID, task_update_request: TaskUpdateRequest
    ) -> TaskResponse:
        task: Task = await self._task_repo.get(task_update_request.id)
        if task.user_id != user_id:
            raise ForbiddenException()
        updated_task_data = task_update_request.model_dump(exclude_unset=True)

        # Avoid triggering validation on every field assignment. Otherwise, this
        # can trigger validation error because of partial attributes update,
        # e.g. if `due_to` is set to `None` before `recurrence` is set to
        # `None`.
        task_data = task.model_dump()
        task_data.update(updated_task_data)
        task = Task.model_validate(task_data)

        await self._task_repo.update_or_create(task)
        return convert_to_response(task)

    async def get_tasks_by_date(
        self,
        user_id: UUID,
        not_before: date,
        not_after: date,
        with_overdue: bool = False,
    ) -> TasksByDatesResponse:
        if not_before > not_after:
            raise IncorrectDateInterval()
        tasks = await self._task_repo.get_tasks_by_due_to(
            not_before=not_before,
            not_after=not_after,
            user_id=user_id,
        )
        tasks_by_dates = divide_tasks_by_dates(tasks, not_before, not_after)
        if with_overdue:
            tasks_by_dates.overdue = await self._task_repo.get_overdue_tasks(user_id)
        return convert_to_response(tasks_by_dates)

    async def get_archived_tasks(self, user_id: UUID) -> ArchivedTasksResponse:
        tasks = await self._task_repo.get_archived_tasks(user_id)
        tasks = ArchivedTasks(tasks=tasks)
        return convert_to_response(tasks)

    async def get_tasks_by_search_query(
        self, user_id: UUID, query: str
    ) -> TaskSearchResponse:
        tasks = await self._task_repo.search(user_id, query)
        return convert_to_response(tasks)


class SectionService:
    def __init__(self, uow: IUnitOfWork):
        self._section_repo = uow.section_repo
        self._task_repo = uow.task_repo

    async def add(self, user_id: UUID, section_data: SectionCreateRequest) -> Section:
        parent_section = await self._section_repo.get(
            section_data.parent_id, with_direct_subsections=True
        )
        if parent_section.user_id != user_id:
            raise ForbiddenException()
        # add to the end of parent section:
        index = await self._section_repo.count_subsections(parent_section.id)

        section = Section(
            user_id=user_id,
            title=section_data.title,
            parent_id=section_data.parent_id,
            tasks=[],
            subsections=[],
            has_subsections=False,
            has_tasks=False,
        )
        parent_section.insert_subsection(
            section, index
        )  # this line checks constraints of parent_section
        await self._section_repo.add(section, index=index)
        await self._section_repo.update(parent_section)
        return section

    # TODO: raise ChangingRootSectionError if root section is being updated
    async def update_section(
        self, user_id: UUID, section_data: SectionUpdateRequest
    ) -> SectionResponse:
        section: Section = await self._section_repo.get(section_data.id)
        if section.user_id != user_id:
            raise ForbiddenException()
        section_data = section_data.model_dump(exclude_unset=True)
        for key, value in section_data.items():
            setattr(section, key, value)
        await self._section_repo.update(section)
        return convert_to_response(section)

    async def get_section(self, user_id: UUID, section_id: UUID) -> SectionResponse:
        section: Section = await self._section_repo.get(section_id)
        if section.user_id != user_id:
            raise ForbiddenException()
        return convert_to_response(section)

    async def get_all_sections(
        self, user_id: UUID, leaves_only: bool, as_tree: bool
    ) -> SectionsListResponse:
        sections: list[Section] = await self._section_repo.get_all_without_tasks(
            user_id, leaves_only=leaves_only, as_tree=as_tree
        )
        # TODO: remove tasks=[] from this schema to avoid confusion! use new
        # schema, e.g. "SectionSummary"
        return convert_to_response(sections)

    async def create_task(self, user_id: UUID, task: TaskCreateRequest) -> UUID:
        task_request = task
        task = Task(
            user_id=user_id,
            section_id=task_request.section_id,
            parent_task_id=task_request.parent_task_id,
            title=task_request.title,
            description=task_request.description,
            is_completed=False,
            due_to=task_request.due_to,
            recurrence=task_request.recurrence,
        )
        section = await self._section_repo.get(task.section_id)
        if section.user_id != user_id:
            raise ForbiddenException()
        if task.parent_task_id is not None:
            parent = await self._task_repo.get(task.parent_task_id)
            if parent.user_id != user_id or parent.section_id != section.id:
                raise ForbiddenException()
        section.insert_task(task)
        await self._section_repo.update(section)
        return task.id

    async def create_tasks_bulk(
        self, user_id: UUID, task_requests: list[TaskCreateRequest]
    ) -> list[UUID]:
        if not task_requests:
            return []
        # assuming tasks[i].section_id are the same:
        assert all(
            task.section_id == task_requests[0].section_id for task in task_requests
        )
        task_ids = []
        tasks = []
        for task_request in task_requests:
            task = Task(
                user_id=user_id,
                section_id=task_request.section_id,
                parent_task_id=task_request.parent_task_id,
                title=task_request.title,
                description=task_request.description,
                is_completed=False,
                due_to=task_request.due_to,
                recurrence=task_request.recurrence,
            )
            task_ids.append(task.id)
            tasks.append(task)
        section = await self._section_repo.get(tasks[0].section_id)
        for task in tasks:
            section.insert_task(task)
        await self._section_repo.update(section)
        return task_ids

    async def remove_task(self, user_id: UUID, task_id: UUID) -> None:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        if await self._task_repo.get_children(task.id):
            raise TaskHasSubtasksError()
        task = section.remove_task(task)
        await self._task_repo.remove(task)
        await self._section_repo.update(section)

    async def move_task(self, user_id: UUID, request: TaskMoveRequest) -> None:
        task = await self._task_repo.get(request.task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section_from = await self._section_repo.get(task.section_id)
        same_section = request.section_to_id == section_from.id
        if same_section:
            section_to = section_from
        else:
            section_to = await self._section_repo.get(request.section_to_id)

        async def collect_descendants(parent_id: UUID) -> list[Task]:
            descendants: list[Task] = []
            for candidate in await self._task_repo.get_children(parent_id):
                descendants.append(candidate)
                descendants.extend(await collect_descendants(candidate.id))
            return descendants

        descendants = await collect_descendants(task.id)

        if section_to.user_id != user_id:
            raise ForbiddenException()
        if request.parent_task_id is not None:
            if request.parent_task_id == task.id:
                raise TaskCantBeOwnParentError()
            parent = await self._task_repo.get(request.parent_task_id)
            if parent.user_id != user_id or parent.section_id != section_to.id:
                raise ForbiddenException()
            ancestor = parent
            while ancestor.parent_task_id is not None:
                if ancestor.parent_task_id == task.id:
                    raise TaskCantBeOwnParentError()
                ancestor = await self._task_repo.get(ancestor.parent_task_id)

        Section.move_task(task, section_from, section_to, request.index)
        task.move_to(section_to.id, request.parent_task_id)

        if not same_section:
            descendant_index = request.index + 1
            for descendant in descendants:
                if descendant.is_archived:
                    descendant.move_to(section_to.id, descendant.parent_task_id)
                    await self._task_repo.update_or_create(descendant, must_exist=True)
                else:
                    section_from.remove_task(descendant)
                    section_to.insert_task(descendant, descendant_index)
                    descendant.move_to(section_to.id, descendant.parent_task_id)
                    descendant_index += 1

        if same_section:
            await self._section_repo.update(section_from)
        else:
            await self._section_repo.update(section_from)
            await self._section_repo.update(section_to)

    async def remove_section(self, user_id: UUID, section_id: UUID) -> None:
        section = await self._section_repo.get(section_id, with_direct_subsections=True)
        if section.user_id != user_id:
            raise ForbiddenException()
        if section.is_root():
            raise ChangingRootSectionError()
        if (
            section.has_tasks
            or section.has_subsections
            or await self._task_repo.has_tasks_in_section(section.id)
        ):
            raise SectionNotEmptyError()
        assert section.parent_id
        parent = await self._section_repo.get(
            section.parent_id, with_direct_subsections=True
        )
        parent.remove_subsection(section)
        await self._section_repo.remove(section)
        await self._section_repo.update(parent)

    async def move_section(self, user_id: UUID, request: SectionMoveRequest) -> None:
        # move `section` from `section_from` to `section to` with given `index``
        section = await self._section_repo.get(
            request.section_id, with_direct_subsections=True
        )
        if section.user_id != user_id:
            raise ForbiddenException()
        if section.is_root():
            raise ChangingRootSectionError()
        assert section.parent_id  # (because it's not root, assert for type checking)
        section_to = await self._section_repo.get(
            request.to_parent_id, with_direct_subsections=True
        )
        if section_to.user_id != user_id:
            raise ForbiddenException()
        same_section = request.to_parent_id == section.parent_id
        if same_section:
            section_from = section_to
        else:
            section_from = await self._section_repo.get(
                section.parent_id, with_direct_subsections=True
            )

        is_valid_moving = await self.is_hierarchically_valid_moving(
            user_id, section.id, section_to.id
        )
        if not is_valid_moving:
            raise MisplaceSectionHierarchyError()

        Section.move_section(section, section_from, section_to, request.index)

        await self._section_repo.update(section)
        if same_section:
            await self._section_repo.update(section_from)
        else:
            await self._section_repo.update(section_from)
            await self._section_repo.update(section_to)

    async def is_hierarchically_valid_moving(
        self, user_id: UUID, section_id: UUID, section_to_id: UUID
    ) -> bool:
        sections = await self._section_repo.get_all_without_tasks(
            user_id=user_id, leaves_only=False, as_tree=False
        )

        def find_section_by_id(section_id: UUID) -> Section:
            return next(s for s in sections if s.id == section_id)

        section_to = find_section_by_id(section_to_id)
        if section_to.id == section_id:
            return False
        s = section_to
        while s.parent_id:
            if s.id == section_id:
                return False
            s = find_section_by_id(s.parent_id)
        return True

    async def toggle_task_completed(
        self, user_id: UUID, task_id: UUID, auto_archive: bool
    ) -> SectionResponse:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)
        task_is_archived_before = task.is_archived

        task.toggle_completed(auto_archive=auto_archive)

        if task.is_archived != task_is_archived_before:
            if task.is_archived:
                # "remove" task from section to update others' indices:
                section.remove_task(task)
            else:
                # unarchiving task => add to section end
                section.insert_task(task)
            await self._section_repo.update(section)
        await self._task_repo.update_or_create(task)
        return convert_to_response(section)

    async def toggle_task_archived(
        self, user_id: UUID, task_id: UUID
    ) -> SectionResponse:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)

        task.toggle_archived()

        if task.is_archived:
            # just became archived =>
            # "remove" task from section to update others' indices:
            section.remove_task(task)
        else:
            # unarchiving task => add to section end
            section.insert_task(task)
        await self._section_repo.update(section)
        await self._task_repo.update_or_create(task)
        return convert_to_response(section)

    async def shuffle(
        self, user_id: UUID, request: ShuffleSectionRequest
    ) -> SectionResponse:
        section = await self._section_repo.get(request.section_id)
        if section.user_id != user_id:
            raise ForbiddenException()
        section.shuffle_tasks()
        await self._section_repo.update(section)
        return convert_to_response(section)

    async def create_root_section(self, user_id: UUID) -> Section:
        section = Section.create_root_section(user_id)
        await self._section_repo.add(section, index=0)
        return section
