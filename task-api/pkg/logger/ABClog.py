from abc import ABC, abstractmethod
from typing import Any


class Logger(ABC):
    """Интерфейс создания логгера"""
    @abstractmethod
    def info(self, msg: Any):
        pass

    @abstractmethod
    def warning(self, msg: Any):
        pass

    @abstractmethod
    def error(self, msg: Any):
        pass
