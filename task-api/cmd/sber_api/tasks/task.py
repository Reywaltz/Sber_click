from dataclasses import dataclass
from datetime import datetime

from flask import Flask, Response, request, jsonify
from werkzeug.datastructures import MultiDict
from internal.exceptions.exception import URLvalidException
from internal.models.task import CreateTask, TaskFull
from cmd.additions.additions import Queries
from internal.repository.tasks.task import TaskRepo
from pkg.logger.log import Log
from psycopg2 import IntegrityError
from pydantic.error_wrappers import ValidationError


@dataclass
class TaskHandler:

    app: Flask
    logger: Log
    task_storage: TaskRepo

    def create_routes(self):
        self.app.add_url_rule(
            rule="/api/v1/tasks",
            endpoint="create_task",
            view_func=self.create_task,
            methods=["POST"]
        )

        self.app.add_url_rule(
            rule="/api/v1/tasks/<id>",
            endpoint="update_task",
            view_func=self.update_task,
            methods=["PUT"]
        )

        self.app.add_url_rule(
            rule="/api/v1/tasks/<id>",
            endpoint="delete_task",
            view_func=self.delete_task,
            methods=["DELETE"]
        )

        self.app.add_url_rule(
            rule="/api/v1/tasks",
            endpoint="get_tasks",
            view_func=self.get_tasks,
            methods=["GET"]
        )

    def create_task(self):
        data = request.get_json(force=True)

        try:
            new_user = CreateTask(**data)
            self.logger.info(new_user)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.task_storage.insert(new_user)

        except IntegrityError as e:
            self.logger.info(f"Can't create task. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't insert: {e}")
            return {"error": "Can't insert"}, 500

        self.logger.info("task created")
        return {"success": "created"}, 201

    def update_task(self, id: int):
        data = request.get_json(force=True)

        try:
            updated_user = TaskFull(id=id, **data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.task_storage.update(updated_user)
        except IntegrityError as e:
            self.logger.error(f"Can't create task: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't update: {e}")
            return {"error": "Can't update task"}, 500

        return {"success": "Updated"}, 204

    def delete_task(self, id: int):
        try:
            id = int(id)
        except ValueError:
            return {"error": "id param is not an int"}, 400

        try:
            self.task_storage.delete(id)
        except Exception as e:
            self.logger.error(f"Can't delete task with id={id}. Error: {e}")
            return {"Error": "Can't delete item"}, 500

        return {"success": "deleted"}, 204

    def get_tasks(self):
        args = request.args

        try:
            q = get_url_params(args)
        except URLvalidException as e:
            self.logger.error(f"bad query param: {e}")
            return {"error": "bad query param"}, 400

        print(q.created, q.type, q.status)

        res = self.task_storage.getall(q)

        return jsonify(res), 200


def get_url_params(params: MultiDict) -> Queries:
    date_param = params.get("date", None)
    date_lst = []

    if date_param is not None and date_param != "":
        tmp = date_param.split(",")
        for date in tmp:
            try:
                date_lst.append(datetime.strptime(date, '%Y-%m-%d'))
            except ValueError:
                raise URLvalidException("Bad date param")
    elif date_param is None:
        date_lst = [datetime.min, datetime.now()]

    if len(date_lst) > 1:
        if date_lst[-1] < date_lst[0]:
            raise URLvalidException("Bad date param")

    type_param = params.get("type", "%%")

    if type_param == "":
        raise URLvalidException("Empty string type param")

    status_param = params.get("status", None)
    status_lst = []

    if status_param is not None:
        if status_param != "":
            status_lst = status_param.split(",")
        else:
            raise URLvalidException("Bad status param")

    return Queries(created=date_lst, type=type_param, status=status_lst)
