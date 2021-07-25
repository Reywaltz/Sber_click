from additions.addition import auth_required
from dataclasses import dataclass

from flask import Flask, Response, request
from internal.models.customer import Customer, CustomerFull
from internal.repository.customer import CustomerRepo
from internal.repository.user import UserRepo
from pkg.log import Log
from psycopg2 import IntegrityError
from pydantic.error_wrappers import ValidationError


@dataclass
class CustomerHandler:

    app: Flask
    logger: Log
    customer_storage: CustomerRepo
    user_storage: UserRepo

    def create_routes(self):
        self.app.add_url_rule(
            rule="/api/v1/customers",
            view_func=self.create_customer,
            methods=["POST"]
        )

        self.app.add_url_rule(
            rule="/api/v1/customers/<id>",
            view_func=self.update_customer,
            methods=["PUT"]
        )

        self.app.add_url_rule(
            rule="/api/v1/customers/<id>",
            view_func=self.delete_customer,
            methods=["DELETE"]
        )

    @auth_required
    def create_customer(self):
        data = request.get_json(force=True)

        username = data.get("username", "")
        tg_name = data.get("tg_name", None)

        if (username == "") and (tg_name is not None) and (tg_name != ""):
            return {"error": "empty fields"}, 400

        try:
            new_user = Customer(**data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.customer_storage.insert(new_user)

        except IntegrityError as e:
            self.logger.info(f"Can't create customer. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't insert: {e}")
            return {"error": "Can't insert"}, 500

        self.logger.info("user created")
        return {"success": "created"}, 201

    @auth_required
    def update_customer(self, id: int):
        data = request.get_json(force=True)

        try:
            updated_user = CustomerFull(id=id, **data)
        except ValidationError as e:
            resp = Response(e.json())
            resp.headers["Content-Type"] = "application/json"
            return resp, 400

        try:
            self.customer_storage.update(updated_user)
        except IntegrityError as e:
            self.logger.error(f"Can't create customer. Already exsists: {e}")
            return {"error": "Already exists"}, 400

        except Exception as e:
            self.logger.error(f"Can't update: {e}")
            return {"error": "Can't update user"}, 500

        return {"success": "Updated"}, 204

    @auth_required
    def delete_customer(self, id: int):
        try:
            id = int(id)
        except ValueError:
            return {"error": "id param is not an int"}, 400

        try:
            self.customer_storage.delete(id)
        except Exception as e:
            self.logger.error(f"Can't delete item with id={id}. Error: {e}")
            return {"Error": "Can't delete item"}, 500

        return {"success": "deleted"}, 204
