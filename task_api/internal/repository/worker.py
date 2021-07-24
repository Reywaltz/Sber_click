from dataclasses import dataclass

from internal.models.worker import Storage, Worker, WorkerFull
from psycopg2.extensions import connection

worker_fields = "name"
insert_worker = f"INSERT INTO worker ({worker_fields}) VALUES (%s)"
update_worker = "UPDATE worker set name=%s WHERE id=%s"
delete_worker = "DELETE FROM worker where id = %s"


@dataclass
class WorkerRepo(Storage):

    db: connection

    def insert(self, worker: Worker):
        cursor = self.db.cursor()
        try:
            cursor.execute(insert_worker, (worker.name,))
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, worker_id: int):
        cursor = self.db.cursor()
        try:
            cursor.execute(delete_worker, (worker_id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, worker: WorkerFull) -> int:
        try:
            cursor = self.db.cursor()
            cursor.execute(update_worker, (worker.name,
                                           worker.id))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def getall(self):
        ...


def new_WorkerRepo(db) -> WorkerRepo:
    return WorkerRepo(db=db)
