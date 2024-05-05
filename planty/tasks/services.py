from planty.tasks.entities import Task


class TaskService:
    def __init__(self, task_repository):
        self._task_repository = task_repository

    def get_task_by_id(self, task_id: int) -> Task:
        return self._task_repository.get_task_by_id(task_id)

    def add_task(self, task: Task) -> None:
        self._task_repository.add_task(task)
