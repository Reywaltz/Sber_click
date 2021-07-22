from abc import ABC, abstractclassmethod

from pydantic import BaseModel


class Customer(BaseModel):
    username: str
    tg_id: int


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
