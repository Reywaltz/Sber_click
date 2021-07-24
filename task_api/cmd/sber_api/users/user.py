from dataclasses import dataclass
from datetime import datetime

from flask import Flask, request
from internal.models.user import User
from internal.repository.users.user import UserRepo
from pkg.logger.log import Log


@dataclass
class UserHandler:

    app: Flask
    logger: Log
    user_storage: UserRepo

    def create_routes(self):
        self.app.add_url_rule(
            rule="/api/v1/login",
            endpoint="log_in",
            view_func=self.login,
            methods=["POST"]
        )

    def login(self):
        data = request.get_json(force=True)

        username = data.get('username', "")
        password = data.get('password', "")

        if (username == "") or (password == ""):
            return {"error": "fields must not be empty"}, 400

        tmp_user = User(username, password, "", datetime.min)

        user_exists = self.user_storage.check_user(tmp_user)
        if user_exists:
            try:
                token = self.user_storage.update_token(tmp_user)
                return {"token": token}, 201
            except Exception as e:
                self.logger.error(f"Can't update token: {e}")
                return {"error": "can't update"}
        else:
            return {"error": "user not found"}, 400
