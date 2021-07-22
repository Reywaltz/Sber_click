from flask import Flask
from pkg.logger.log import init_logger
from cmd.sber_api.customers.customer import CustomerHandler
from cmd.sber_api.workers.worker import WorkerHandler
from internal.repository.customers.customer import new_UserRepo
from internal.repository.workers.worker import new_WorkerRepo
from pkg.postgres.db import newDB, Config, parse_from_connstr

app = Flask("task-api")

logger = init_logger("sber-log")

conn_params = parse_from_connstr("postgres://sber:sber@localhost:5433/sber")
cfg = Config(**conn_params)
db = newDB(cfg=cfg)

customer_repo = new_UserRepo(db)
worker_repo = new_WorkerRepo(db)

customer_handler = CustomerHandler(app, logger, customer_repo)
worker_handler = WorkerHandler(app, logger, worker_repo)

customer_handler.create_routes()
worker_handler.create_routes()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
