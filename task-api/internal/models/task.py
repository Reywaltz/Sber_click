from abc import ABC, abstractclassmethod
from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    name: str
    type: str
    status: str
    date: datetime
    customer_id: int
    worker_id: int


class TaskFull(Task):
    id: int


class Storage(ABC):
    """Интерфейс репозитория"""

    @abstractclassmethod
    def insert(self, task: Task):
        ...

    @abstractclassmethod
    def update(self, task: TaskFull):
        ...

    @abstractclassmethod
    def delete(self, task_id: int):
        ...

    @abstractclassmethod
    def getall(self) -> list[TaskFull]:
        ...
