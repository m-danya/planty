from fastapi import status
from planty.application.exceptions import PlantyException


class MovingTaskIndexError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The task can't be moved to the specified index"
