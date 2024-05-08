from abc import ABC, abstractmethod

from planty.tasks.domain.entities import Task


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...
