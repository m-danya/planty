from typing import Union, cast, overload

from fastapi.encoders import jsonable_encoder

from typing import get_origin, get_args


from planty.application.schemas import (
    ArchivedTasks,
    SectionResponse,
    TaskSearchResponse,
    TaskResponse,
    SectionsListResponse,
    ArchivedTasksResponse,
    TasksByDatesResponse,
    TasksByDates,
)
from planty.application.services.attachments import (
    get_attachment_url,
)
from planty.domain.task import Section, Task
from typing import Any

# NOTE: mypy + singledispatch + overload doesn't work at the same time..

possible_in_types = Union[
    Task, Section, list[Section], TasksByDates, list[Task], ArchivedTasks
]
possible_out_types = Union[
    TaskSearchResponse,
    TaskResponse,
    SectionResponse,
    SectionsListResponse,
    TasksByDatesResponse,
    ArchivedTasksResponse,
]


@overload
def convert_to_response(obj: Task) -> TaskResponse: ...


@overload
def convert_to_response(obj: Section) -> SectionResponse: ...


@overload
def convert_to_response(obj: list[Section]) -> SectionsListResponse: ...


@overload
def convert_to_response(obj: TasksByDates) -> TasksByDatesResponse: ...


@overload
def convert_to_response(obj: list[Task]) -> TaskSearchResponse: ...


@overload
def convert_to_response(obj: ArchivedTasks) -> ArchivedTasksResponse: ...


# TODO: think about returning dict without casting to pydantic model:
# https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file#fastapi-response-serialization


def convert_to_response(obj: possible_in_types) -> possible_out_types:
    if _satisfies(obj, Task):
        obj = cast(Task, obj)
        task_data = obj.model_dump()
        _adjust_task_dict(task_data)
        return TaskResponse(**task_data)
    elif _satisfies(obj, Section):
        obj = cast(Section, obj)
        section_data = obj.model_dump()
        _adjust_section_dict(section_data)
        return SectionResponse(**section_data)
    elif _satisfies(obj, ArchivedTasks):
        obj = cast(ArchivedTasks, obj)
        archived_data = obj.model_dump()
        for task in archived_data.get("tasks", []):
            _adjust_task_dict(task)
        return ArchivedTasksResponse(**archived_data)
    elif _satisfies(obj, list[Task]):
        obj = cast(list[Task], obj)
        return [convert_to_response(obj_item) for obj_item in obj]
    elif _satisfies(obj, list[Section]):
        obj = cast(list[Section], obj)
        return [convert_to_response(obj_item) for obj_item in obj]
    elif _satisfies(obj, TasksByDates):
        obj = cast(TasksByDates, obj)
        tasks_by_dates = jsonable_encoder(obj)
        for task_by_date in tasks_by_dates:
            for task in task_by_date["tasks"]:
                _adjust_task_dict(task)
        tasks_by_dates: TasksByDatesResponse
        return tasks_by_dates
    else:
        raise NotImplementedError(
            f"Unsupported type for converting into response schema: {type(obj)}"
        )


def _adjust_task_dict(task: dict[str, Any]) -> None:
    task.pop("user_id")
    for attachment in task.get("attachments", []):
        attachment["url"] = get_attachment_url(attachment["s3_file_key"])


def _adjust_section_dict(section: dict[str, Any]) -> None:
    section.pop("user_id")
    section.pop("has_tasks")
    section.pop("has_subsections")
    for task in section.get("tasks", []):
        _adjust_task_dict(task)
    for subsection in section.get("subsections", []):
        _adjust_section_dict(subsection)


def _satisfies(obj: Any, type_hint: Any) -> bool:
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is None:
        return isinstance(obj, type_hint)
    elif origin is Union:
        return any(_satisfies(obj, arg) for arg in args)
    elif origin is list:
        if not isinstance(obj, list):
            return False
        return all(_satisfies(item, args[0]) for item in obj)
    elif origin is dict:
        if not isinstance(obj, dict):
            return False
        key_type, value_type = args
        return all(
            _satisfies(k, key_type) and _satisfies(v, value_type)
            for k, v in obj.items()
        )
    else:
        raise NotImplementedError("Unexpected generic type")
