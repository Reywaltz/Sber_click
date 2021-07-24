import logging
from typing import Any

from pkg.logger.ABClog import Logger


class Log(Logger):
    """Основной логгер"""
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def info(self, msg: Any):
        self.logger.info(msg)

    def warning(self, msg: Any):
        self.logger.info(msg)

    def error(self, msg: Any):
        self.logger.error(msg)


def init_logger(logger_name: str) -> Log:
    """Метод инициализации консольного логгера

    :param logger_name: имя логгера
    :type logger_name: str
    :return: консольный логгер
    :rtype: Log
    """
    log = logging.getLogger(logger_name)
    log.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)

    handler.setFormatter(formatter)
    log.addHandler(handler)

    logger = Log(logger=log)
    return logger
