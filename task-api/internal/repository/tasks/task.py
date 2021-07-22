from dataclasses import dataclass
from internal.models.task import CreateTask, Storage, TaskFull
from pkg.postgres.db import DB
from psycopg2.extras import DictCursor

task_fields = "name, type, status, date, customer_id"
get_tasks = "SELECT * FROM task order by id"
insert_task = f"INSERT INTO task ({task_fields}) VALUES (%s, %s, %s, %s, %s)"
update_task = "UPDATE task set name=%s, type=%s, status=%s, date=%s,\
               customer_id=%s, worker_id=%s where id=%s"
delete_task = "DELETE FROM task where id = %s"


@dataclass
class TaskRepo(Storage):

    db: DB

    def insert(self, task: CreateTask):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(insert_task, (task.name,
                                         task.type,
                                         task.status,
                                         task.date,
                                         task.customer_id,))
            self.db.session.commit()

        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete(self, task_id: int):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(delete_task, (task_id,))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def update(self, task: TaskFull):
        try:
            cursor = self.db.session.cursor()
            cursor.execute(update_task, (task.name,
                                         task.type,
                                         task.status,
                                         task.date,
                                         task.customer_id,
                                         task.worker_id,
                                         task.id))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def getall(self):
        cursor = self.db.session.cursor(cursor_factory=DictCursor)
        cursor.execute(get_tasks)
        res = cursor.fetchall()
        res = scan_tasks(res)

        return res


def scan_tasks(res: list[tuple]) -> list[TaskFull]:
    out = []
    for task in res:
        out.append(scan_task(task))

    return out


def scan_task(res: dict) -> TaskFull:
    return TaskFull(**res).dict()


def new_TaskRepo(db: DB) -> TaskRepo:
    return TaskRepo(db=db)
