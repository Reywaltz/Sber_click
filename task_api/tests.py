import random
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import psycopg2
import pytest
from flask import Flask

from customer import CustomerHandler
from internal.repository import customer, task, user, worker
from pkg.db import Config, newDB, parse_from_connstr
from pkg.log import init_logger
from task import TaskHandler
from user import UserHandler
from worker import WorkerHandler


class Test_ParseConnStr:

    def test_parse_from_number(self):
        rand = random.randint(-10, 10)
        with pytest.raises(TypeError):
            parse_from_connstr(rand)

    def test_parse_from_empty_string(self):
        with pytest.raises(psycopg2.ProgrammingError):
            parse_from_connstr("")

    def test_parse_invalid_dsn(self):
        params = {
            "user": "sber",
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


def init(db: MagicMock):

    app = Flask("test")

    logger = init_logger("test")

    customer_repo = customer.new_CustomerRepo(db)
    worker_repo = worker.new_WorkerRepo(db)
    task_repo = task.new_TaskRepo(db)
    user_repo = user.new_UserRepo(db)

    customer_handler = CustomerHandler(app, logger, customer_repo, user_repo)
    worker_handler = WorkerHandler(app, logger, worker_repo, user_repo)
    task_handler = TaskHandler(app, logger, task_repo, user_repo)
    user_handler = UserHandler(app, logger, user_repo)

    customer_handler.create_routes()
    worker_handler.create_routes()
    task_handler.create_routes()
    user_handler.create_routes()

    return app


class Test_User_Handler:
    def test_ok_login(self):

        test_hash = '$2b$12$TVug7gxMJubntOvSZ.pbduu3PDHaQBx/dk3PjtzviOB50fB1G4Yp2'
        db = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = ("admin",
                                        test_hash,
                                        datetime.now(),
                                        str(uuid4()))

        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {"username": "admin", "password": "test"}

        test_cl = app.test_client()
        with test_cl.post("/api/v1/login", json=inp_json) as req:
            assert req.status_code == 201

    def test_not_exsist_login(self):

        db = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {"username": "admin", "password": "test"}

        test_cl = app.test_client()
        with test_cl.post("/api/v1/login", json=inp_json) as req:
            assert req.status_code == 400

    def test_bad_json(self):

        db = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {"key1": "admin", "key2": "test"}

        test_cl = app.test_client()
        with test_cl.post("/api/v1/login", json=inp_json) as req:
            assert req.status_code == 400


class Test_Task_Handler:
    def test_ok_add(self):

        test_token = str(uuid4())
        valid_to = datetime.now(tz=ZoneInfo("UTC")) + timedelta(hours=1)
        db = MagicMock()
        cursor = MagicMock()
        header = {"Authorization": f"Bearer {test_token}"}
        cursor.fetchone.return_value = ("admin", "pass", test_token, valid_to)

        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {
            "name": "Посмотреть",
            "type": "Анализ",
            "status": "В процессе",
            "customer_id": "1",
            "created": "2021-07-23 22:44:48.974729"
        }

        test_cl = app.test_client()
        with test_cl.post("/api/v1/tasks", json=inp_json, headers=header) as req:
            assert req.status_code == 201

    def test_token_expired(self):

        test_token = str(uuid4())
        valid_to = datetime.now(tz=ZoneInfo("UTC")) - timedelta(hours=1)
        db = MagicMock()
        cursor = MagicMock()
        header = {"Authorization": f"Bearer {test_token}"}
        cursor.fetchone.return_value = ("admin", "pass", test_token, valid_to)

        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {
            "name": "Посмотреть",
            "type": "Анализ",
            "status": "В процессе",
            "customer_id": "1",
            "created": "2021-07-23 22:44:48.974729"
        }

        test_cl = app.test_client()
        with test_cl.post("/api/v1/tasks", json=inp_json, headers=header) as req:
            assert req.status_code == 401

    def test_no_token(self):

        db = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None

        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {
            "name": "Посмотреть",
            "type": "Анализ",
            "status": "В процессе",
            "customer_id": "1",
            "created": "2021-07-23 22:44:48.974729"
        }

        test_cl = app.test_client()
        with test_cl.post("/api/v1/tasks", json=inp_json) as req:
            assert req.status_code == 401

    def test_invalid_json(self):
        test_token = str(uuid4())
        valid_to = datetime.now(tz=ZoneInfo("UTC")) + timedelta(hours=1)
        db = MagicMock()
        cursor = MagicMock()
        header = {"Authorization": f"Bearer {test_token}"}
        cursor.fetchone.return_value = ("admin", "pass", test_token, valid_to)

        db.cursor.return_value = cursor

        app = init(db)

        inp_json = {
            "name": "Посмотреть",
            "type": "Анализ",
            "status": "В процессе",
            "customer_id": "SOMEWRONG",
            "created": "2021-07-23 22:44:48.974729"
        }

        test_cl = app.test_client()
        with test_cl.post("/api/v1/tasks", json=inp_json, headers=header) as req:
            assert req.status_code == 400
