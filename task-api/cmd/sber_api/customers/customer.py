from dataclasses import dataclass

from flask import Flask, Response, request
from internal.models.customer import Customer, CustomerFull
from internal.repository.customers.customer import CustomerRepo
from pkg.logger.log import Log
from psycopg2 import IntegrityError
from pydantic.error_wrappers import ValidationError


@dataclass
class CustomerHandler:

    app: Flask
    logger: Log
    user_storage: CustomerRepo

    def create_routes(self):
        self.app.add_url_rule(
            "/api/v1/customer",
            "create_customer",
            self.create,
            methods=["POST"]
        )

        self.app.add_url_rule(
            "/api/v1/customer/<id>",
            "update_customer",
            self.update,
            methods=["PUT"]
        )

        self.app.add_url_rule(
            "/api/v1/customer/<id>",
            "delete_customer",
            self.delete,
            methods=["DELETE"]
        )

    def create(self):
        data = request.get_json(force=True)

        try:
            new_user = Customer(**data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.user_storage.insert(new_user)

        except IntegrityError as e:
            self.logger.info(f"Can't create customer. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't insert: {e}")
            return {"error": "Can't insert"}, 500

        self.logger.info("user created")
        return {"success": "created"}, 201

    def update(self, id: int):
        data = request.get_json(force=True)

        try:
            updated_user = CustomerFull(id=id, **data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.user_storage.update(updated_user)
        except IntegrityError as e:
            self.logger.error(f"Can't create customer. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't update: {e}")
            return {"error": "Can't update user"}, 500

        return {"success": "Updated"}, 204

    def delete(self, id: int):
        try:
            id = int(id)
        except ValueError:
            return {"error": "id param is not an int"}, 400

        try:
            self.user_storage.delete(id)
        except Exception as e:
            self.logger.error(f"Can't delete item with id={id}. Error: {e}")
            return {"Error": "Can't delete item"}, 500

        return {"success": "deleted"}, 204
