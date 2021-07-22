from dataclasses import dataclass

from flask import Flask, Response, request, jsonify
from internal.models.task import CreateTask, TaskFull
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
        res = self.task_storage.getall()

        return jsonify(res), 200
