from typing import Any
from fastapi import HTTPException, status


class PlantyException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self._detail if hasattr(self, "_detail") else self.detail,
        )


class EntityNotFoundException(PlantyException):
    status_code = status.HTTP_404_NOT_FOUND
    entity_name = "entity"

    def __init__(self, **filter_criteria: Any) -> None:  # TODO: replace Any with smth
        self.filter_criteria = filter_criteria
        super().__init__()

    @property
    def _detail(self) -> str:
        return f"There is no {self.entity_name} with {self.filter_criteria}"


class UserNotFoundException(EntityNotFoundException):
    entity_name = "user"


class TaskNotFoundException(EntityNotFoundException):
    entity_name = "user"
