from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    username: str
    password: str
    token: str
    valid_to: datetime


class Storage(ABC):
    """Интерфейс репозитория"""

    @abstractclassmethod
    def check_user(self, user: User):
        ...

    @abstractclassmethod
    def check_token(self, user: User):
        ...

    @abstractclassmethod
    def update_token(self, user: User):
        ...

    