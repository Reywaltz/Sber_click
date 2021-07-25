from additions.addition import auth_required, get_url_params
from dataclasses import dataclass

from flask import Flask, Response, jsonify, request
from internal.exception import URLvalidException
from internal.models.task import CreateTask, TaskFull
from internal.repository.task import TaskRepo
from internal.repository.user import UserRepo
from pkg.log import Log
from psycopg2 import IntegrityError
from pydantic.error_wrappers import ValidationError


@dataclass
class TaskHandler:

    app: Flask
    logger: Log
    task_storage: TaskRepo
    user_storage: UserRepo

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

    @auth_required
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

    @auth_required
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

    @auth_required
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

    @auth_required
    def get_tasks(self):
        args = request.args

        try:
            q = get_url_params(args)
        except URLvalidException as e:
            self.logger.error(f"bad query param: {e}")
            return {"error": "bad query param"}, 400

        res = self.task_storage.getall(q)

        return jsonify(res), 200
