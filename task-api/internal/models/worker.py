from abc import ABC, abstractclassmethod

from pydantic import BaseModel


class Worker(BaseModel):
    name: str


class WorkerFull(Worker):
    id: int


class Storage(ABC):
    """Интерфейс репозитория"""

    @abstractclassmethod
    def insert(self, worker: Worker):
        ...

    @abstractclassmethod
    def update(self, worker: WorkerFull):
        ...

    @abstractclassmethod
    def delete(self, worker_id: int):
        ...
