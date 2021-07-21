import psycopg2
from psycopg2.extensions import connection
from dataclasses import dataclass


@dataclass
class Config:
    database: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class DB:
    session: connection

    def close(self):
        self.session.close()


def newDB(cfg: Config) -> DB:
    conn = psycopg2.connect(
        database=cfg.database,
        user=cfg.user,
        password=cfg.password,
        host=cfg.host,
        port=cfg.port
    )
    db = DB(session=conn)
    return db
