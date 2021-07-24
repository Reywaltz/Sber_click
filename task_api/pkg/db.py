from dataclasses import dataclass

import psycopg2
from psycopg2 import ProgrammingError
from psycopg2.extensions import connection, parse_dsn


@dataclass
class Config:
    dbname: str
    user: str
    password: str
    host: str
    port: str


def parse_from_connstr(connURI: str) -> dict:
    if connURI == "":
        raise ProgrammingError
    try:
        return parse_dsn(connURI)
    except ProgrammingError:
        raise ProgrammingError
    except TypeError:
        raise TypeError


@dataclass
class DB:
    session: connection

    def close(self):
        self.session.close()


def newDB(cfg: Config) -> DB:
    try:
        conn = psycopg2.connect(
            database=cfg.dbname,
            user=cfg.user,
            password=cfg.password,
            host=cfg.host,
            port=cfg.port
        )
    except psycopg2.OperationalError as e:
        raise e
    # db = DB(session=conn)
    return conn
