import pytest
import psycopg2
import random
from task_api.pkg.postgres.db import parse_from_connstr
from task_api.pkg.postgres.db import newDB, Config


class Test_ParseConnStr:

    def test_parse_from_number(self):
        rand = random.randint(-10, 10)
        with pytest.raises(TypeError):
            parse_from_connstr(rand)

    def test_parse_from_empty_string(self):
        with pytest.raises(psycopg2.ProgrammingError):
            parse_from_connstr("")

    def test_parse_invalid_dsn(self):
        params = {"user": "sber",
                  "password": "sber",
                  "dbname": "sber",
                  "host": "db",
                  "port": "5432",
                  }

        conn = "postszgres://{0}:{1}@{2}:{3}/{4}".format(params["user"],
                                                         params["password"],
                                                         params["host"],
                                                         params["port"],
                                                         params["dbname"])

        with pytest.raises(psycopg2.ProgrammingError):
            parse_from_connstr(conn)

    def test_parse_valid_dsn(self):
        params = {"user": "sber",
                  "password": "sber",
                  "dbname": "sber",
                  "host": "db",
                  "port": "5432",
                  }

        conn = "postgres://{0}:{1}@{2}:{3}/{4}".format(params["user"],
                                                       params["password"],
                                                       params["host"],
                                                       params["port"],
                                                       params["dbname"])

        actual = parse_from_connstr(conn)

        assert params == actual


class Test_DB:
    def test_conn_with_wrong_credits(self):
        params = {
            "user": "SOMEWRONGCREADENTIALS",
            "password": "SOMEWRONGCREADENTIALS",
            "dbname": "SOMEWRONGCREADENTIALS",
            "host": "SOMEWRONGCREADENTIALS",
            "port": "SOMEWRONGCREADENTIALS",
        }

        cfg = Config(**params)
        with pytest.raises(psycopg2.OperationalError):
            newDB(cfg)

    def test_conn_with_ok_credits(self):
        params = {
            "user": "sber",
            "password": "sber",
            "dbname": "sber",
            "host": "localhost",
            "port": "5433",
        }

        cfg = Config(**params)

        assert newDB(cfg) is not None
