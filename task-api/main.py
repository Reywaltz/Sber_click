from cmd.sber_api.customers.customer import CustomerHandler
from cmd.sber_api.tasks.task import TaskHandler
from cmd.sber_api.workers.worker import WorkerHandler
from cmd.sber_api.users.user import UserHandler

from flask import Flask

from internal.repository.customers.customer import new_CustomerRepo
from internal.repository.tasks.task import new_TaskRepo
from internal.repository.workers.worker import new_WorkerRepo
from internal.repository.users.user import new_UserRepo
from pkg.logger.log import init_logger
from pkg.postgres.db import Config, newDB, parse_from_connstr

app = Flask("task-api")

logger = init_logger("sber-log")

conn_params = parse_from_connstr("postgres://sber:sber@localhost:5433/sber")
cfg = Config(**conn_params)
db = newDB(cfg=cfg)

customer_repo = new_CustomerRepo(db)
worker_repo = new_WorkerRepo(db)
task_repo = new_TaskRepo(db)
user_repo = new_UserRepo(db)


customer_handler = CustomerHandler(app, logger, customer_repo)
worker_handler = WorkerHandler(app, logger, worker_repo)
task_handler = TaskHandler(app, logger, task_repo)
user_handler = UserHandler(app, logger, user_repo)


customer_handler.create_routes()
worker_handler.create_routes()
task_handler.create_routes()
user_handler.create_routes()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
