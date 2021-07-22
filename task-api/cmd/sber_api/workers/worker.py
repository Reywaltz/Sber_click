from dataclasses import dataclass

from flask import Flask, Response, request
from internal.models.worker import Worker, WorkerFull
from internal.repository.workers.worker import WorkerRepo
from pkg.logger.log import Log
from psycopg2 import IntegrityError
from pydantic.error_wrappers import ValidationError


@dataclass
class WorkerHandler:

    app: Flask
    logger: Log
    worker_storage: WorkerRepo

    def create_routes(self):
        self.app.add_url_rule(
            rule="/api/v1/workers",
            endpoint="create_worker",
            view_func=self.create_worker,
            methods=["POST"]
        )

        self.app.add_url_rule(
            rule="/api/v1/workers/<id>",
            endpoint="update_worker",
            view_func=self.update_worker,
            methods=["PUT"]
        )

        self.app.add_url_rule(
            rule="/api/v1/workers/<id>",
            endpoint="delete_worker",
            view_func=self.delete_worker,
            methods=["DELETE"]
        )

    def create_worker(self):
        data = request.get_json(force=True)

        try:
            new_user = Worker(**data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.user_storage.insert(new_user)

        except IntegrityError as e:
            self.logger.info(f"Can't create worker. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't insert: {e}")
            return {"error": "Can't insert"}, 500

        self.logger.info("user created")
        return {"success": "created"}, 201

    def update_worker(self, id: int):
        data = request.get_json(force=True)

        try:
            updated_user = WorkerFull(id=id, **data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.user_storage.update(updated_user)
        except IntegrityError as e:
            self.logger.error(f"Can't create worker. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't update: {e}")
            return {"error": "Can't update worker"}, 500

        return {"success": "Updated"}, 204

    def delete_worker(self, id: int):
        try:
            id = int(id)
        except ValueError:
            return {"error": "id param is not an int"}, 400

        try:
            self.user_storage.delete(id)
        except Exception as e:
            self.logger.error(f"Can't delete worker with id={id}. Error: {e}")
            return {"Error": "Can't delete item"}, 500

        return {"success": "deleted"}, 204
