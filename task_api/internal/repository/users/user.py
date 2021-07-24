import uuid
from cmd.additions import additions
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from internal.models.user import Storage, User
from pkg.postgres.db import DB

worker_fields = "username, password, token, valid_to"
get_user_query = f"SELECT {worker_fields} from users where\
                 username=%s"
user_by_token_query = f"SELECT {worker_fields} from users where token=%s"
update_token_query = "UPDATE users set token=%s, valid_to=%s where\
                      username=%s returning token"


@dataclass
class UserRepo(Storage):

    db: DB

    def check_user(self, user: User) -> bool:
        cursor = self.db.session.cursor()

        cursor.execute(get_user_query, (user.username,))
        row = cursor.fetchone()
        if row is not None:
            tmp = User(*row)

            valid_pass = additions.check_password(user.password,
                                                  tmp.password,)
            if valid_pass:
                return True
        return False

    def check_token(self, token: str) -> Optional[User]:
        cursor = self.db.session.cursor()
        cursor.execute(user_by_token_query, (token,))
        row = cursor.fetchone()
        if row is not None:
            return scan_user(row)

        return None

    def update_token(self, user: User) -> str:
        cursor = self.db.session.cursor()
        user.token = str(uuid.uuid4())
        user.valid_to = datetime.now() + timedelta(hours=1)
        cursor.execute(update_token_query, (user.token,
                                            user.valid_to,
                                            user.username,))
        row = cursor.fetchone()
        if row is not None:
            try:
                self.db.session.commit()
                return row[0]
            except Exception:
                self.db.session.rollback()


def scan_user(row: tuple) -> User:
    return User(*row)


def new_UserRepo(db: DB) -> UserRepo:
    return UserRepo(db=db)
