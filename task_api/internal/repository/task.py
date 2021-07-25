from additions.addition import Queries
from dataclasses import dataclass

from internal.models.task import CreateTask, Storage, TaskFull
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

task_fields = "name, type, status, created, customer_id, worker_id"
full_task_fields = "id, " + task_fields
get_base = f"SELECT {full_task_fields} FROM task WHERE"
insert_task = "INSERT INTO task\
              (name, type, status, created, customer_id)\
              VALUES (%s, %s, %s, %s, %s)"
update_task = "UPDATE task set name=%s, type=%s, status=%s, date=%s,\
               customer_id=%s, worker_id=%s where id=%s"
delete_task = "DELETE FROM task where id = %s"


@dataclass
class TaskRepo(Storage):

    db: connection

    def insert(self, task: CreateTask):
        cursor = self.db.cursor()
        try:
            cursor.execute(insert_task, (task.name,
                                         task.type,
                                         task.status,
                                         task.created,
                                         task.customer_id,))
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, task_id: int):
        cursor = self.db.cursor()
        try:
            cursor.execute(delete_task, (task_id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, task: TaskFull):
        try:
            cursor = self.db.cursor()
            cursor.execute(update_task, (task.name,
                                         task.type,
                                         task.status,
                                         task.created,
                                         task.customer_id,
                                         task.worker_id,
                                         task.id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def getall(self, queries: Queries) -> list[TaskFull]:
        cursor = self.db.cursor(cursor_factory=DictCursor)
        query = buildSQL(queries)
        if queries.status != []:
            cursor.execute(query, (queries.created[0],
                                   queries.created[-1],
                                   queries.type,
                                   tuple(queries.status),))
        else:
            cursor.execute(query, (queries.created[0],
                                   queries.created[-1],
                                   queries.type,))


        res = scan_tasks(cursor.fetchall())

        return res


def scan_tasks(res: list[tuple]) -> list[TaskFull]:
    out = []
    for task in res:
        out.append(scan_task(task))

    return out


def scan_task(res: dict) -> TaskFull:
    return TaskFull(**res).dict()


def buildSQL(queries: Queries):
    query = "SELECT * FROM task WHERE DATE(created) between %s and %s and\
            type ilike %s"

    if queries.status != []:
        query = f"{query} and status in %s"

    return query


def new_TaskRepo(db) -> TaskRepo:
    return TaskRepo(db=db)
