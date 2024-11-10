from fastapi import status
from planty.application.exceptions import PlantyException


class MovingTaskIndexError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The task can't be moved to the specified index"


class MisplaceSectionIndexError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The section can't be placed at the specified index"


class RemovingTaskFromWrongSectionError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "This task doesn't belong to this section"


class RemovingSectionFromWrongSectionError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "This section doesn't belong to this section"


class ChangingRootSectionError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The root section can't be modified"


class SectionCantBothHaveTasksAndSubsection(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "Section can't have both tasks and subsections"
