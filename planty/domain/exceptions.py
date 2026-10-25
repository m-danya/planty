from fastapi import status
from planty.application.exceptions import PlantyException


class MovingTaskIndexError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The task can't be moved to the specified index"


class RecurrenceWithoutDueDate(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "Recurrence settings can't be set unless a due date is specified."


class MisplaceSectionIndexError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The section can't be placed at the specified index"


class MisplaceSectionHierarchyError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "The section can't be placed as a subsection of its own subsection"


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


class TaskCantBeOwnParentError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "A task can't be placed inside itself or its subtask"


class SectionNotEmptyError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "Only an empty section without subsections can be removed"


class TaskHasSubtasksError(PlantyException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    @property
    def _detail(self) -> str:
        return "A task with subtasks can't be removed"
