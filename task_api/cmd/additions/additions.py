from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo

import bcrypt
from flask import request
from internal.exceptions.exception import URLvalidException
from pydantic import BaseModel
from werkzeug.datastructures import MultiDict

tz = ZoneInfo("UTC")


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

        if cur_user.valid_to > datetime.now(tz=tz):
            return fn(self, **kwargs)
        else:
            return {"error": "token expired"}, 401

    return wrapper


def get_url_params(params: MultiDict) -> Queries:
    date_param = params.get("date", None)
    date_lst = get_URLdate(date_param)

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


def get_URLdate(date_param: str):
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

    return date_lst


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("UTF-8"), salt)

    return hashed


def check_password(password: str, hash: str) -> bool:
    if bcrypt.checkpw(password.encode("UTF-8"), hash.encode("UTF-8")):
        return True
    return False
