from abc import ABC, abstractclassmethod
from typing import Optional

from pydantic import BaseModel


class Customer(BaseModel):
    name: str
    tg_id: Optional[int]
    tg_name: Optional[str]
    tg_chat: Optional[int]


class CustomerFull(Customer):
    id: int


class Storage(ABC):
    """Интерфейс репозитория"""

    @abstractclassmethod
    def insert(self, customer: Customer):
        ...

    @abstractclassmethod
    def update(self, customer: CustomerFull):
        ...

    @abstractclassmethod
    def delete(self, customer_id: int):
        ...
