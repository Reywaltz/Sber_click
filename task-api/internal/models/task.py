from abc import ABC, abstractclassmethod
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CreateTask(BaseModel):
    name: str
    type: str
    status: str
    created: datetime
    customer_id: int


class TaskWithWorker(CreateTask):
    worker_id: Optional[int]


class TaskFull(TaskWithWorker):
    id: int


class Storage(ABC):
    """Интерфейс репозитория"""

    @abstractclassmethod
    def insert(self, task: CreateTask):
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
