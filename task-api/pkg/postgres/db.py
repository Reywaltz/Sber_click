import psycopg2
from psycopg2.extensions import connection, parse_dsn
from psycopg2 import ProgrammingError
from dataclasses import dataclass


@dataclass
class Config:
    dbname: str
    user: str
    password: str
    host: str
    port: str


def parse_from_connstr(connURI: str) -> dict:
    try:
        return parse_dsn(connURI) 
    except ProgrammingError:
        raise ProgrammingError


@dataclass
class DB:
    session: connection

    def close(self):
        self.session.close()


def newDB(cfg: Config) -> DB:
    conn = psycopg2.connect(
        database=cfg.dbname,
        user=cfg.user,
        password=cfg.password,
        host=cfg.host,
        port=cfg.port
    )
    db = DB(session=conn)
    return db
