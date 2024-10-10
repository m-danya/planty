from datetime import date
from typing import Union, overload

from fastapi.encoders import jsonable_encoder


from planty.application.schemas import (
    SectionResponse,
    TaskResponse,
    SectionsListResponse,
    TasksByDateResponse,
)
from planty.application.services.attachments import (
    get_attachment_url,
)
from planty.domain.task import Section, Task
from typing import Any

# NOTE: mypy + singledispatch + overload doesn't work at the same time..

possible_in_types = Union[Task, Section, list[Section], dict[date, list[Task]]]
possible_out_types = Union[
    TaskResponse, SectionResponse, SectionsListResponse, TasksByDateResponse
]


@overload
def convert_to_response(obj: Task) -> TaskResponse: ...


@overload
def convert_to_response(obj: Section) -> SectionResponse: ...


@overload
def convert_to_response(obj: list[Section]) -> SectionsListResponse: ...


@overload
def convert_to_response(obj: dict[date, list[Task]]) -> TasksByDateResponse: ...


def convert_to_response(obj: possible_in_types) -> possible_out_types:
    if isinstance(obj, Task):
        task_data = obj.model_dump()
        _adjust_task_dict(task_data)
        return TaskResponse(**task_data)
    elif isinstance(obj, Section):
        section_data = obj.model_dump()
        for task in section_data.get("tasks", []):
            _adjust_task_dict(task)
        return SectionResponse(**section_data)
    elif isinstance(obj, list) and all(isinstance(item, Section) for item in obj):
        return [convert_to_response(section) for section in obj]
    elif isinstance(obj, dict) and all(
        isinstance(key, date)
        and isinstance(tasks_list, list)
        and all(isinstance(t, Task) for t in tasks_list)
        for key, tasks_list in obj.items()
    ):
        tasks_by_date = jsonable_encoder(obj)
        for date_ in tasks_by_date:
            for task in tasks_by_date[date_]:
                _adjust_task_dict(task)
        tasks_by_date: TasksByDateResponse
        return tasks_by_date
    else:
        raise NotImplementedError(
            f"Unsupported type for converting into response schema: {type(obj)}"
        )


def _adjust_task_dict(task: dict[str, Any]) -> None:
    for attachment in task.get("attachments", []):
        attachment["url"] = get_attachment_url(attachment["s3_file_key"])
