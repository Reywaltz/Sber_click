from dataclasses import dataclass
from internal.models.worker import Worker, Storage, WorkerFull
from pkg.postgres.db import DB


worker_fields = "name"
insert_worker = f"INSERT INTO worker ({worker_fields}) VALUES (%s)"
update_worker = "UPDATE worker set name=%s, id=%s"
delete_worker = "DELETE FROM worker where id = %s"


@dataclass
class WorkerRepo(Storage):

    db: DB

    def insert(self, worker: Worker):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(insert_worker, (worker.name))
            self.db.session.commit()

        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete(self, worker_id: int):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(delete_worker, (worker_id,))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def update(self, worker: WorkerFull) -> int:
        try:
            cursor = self.db.session.cursor()
            cursor.execute(update_worker, (worker.name,
                                           worker.id))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def getall(self):
        ...


def new_WorkerRepo(db: DB) -> WorkerRepo:
    return WorkerRepo(db=db)
