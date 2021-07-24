from datetime import datetime
from pydantic import BaseModel
from functools import wraps
from flask import request
import bcrypt


class Queries(BaseModel):
    created: list[datetime]
    type: str
    status: list[str]


def auth_required(fn):
    @wraps(fn)
    def wrapper(self, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return {"error": "no auth"}, 401

        token = auth_header.split(' ')[-1]

        cur_user = self.user_storage.check_token(token)
        if cur_user is None:
            return {"error": "no auth"}, 401

        if cur_user.valid_to > datetime.now():
            return fn(self, **kwargs)
        else:
            return {"error": "no auth"}

    return wrapper


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("UTF-8"), salt)

    return hashed


def check_password(password: str, hash: str) -> bool:
    if bcrypt.checkpw(password.encode("UTF-8"), hash.encode("UTF-8")):
        return True
    return False
