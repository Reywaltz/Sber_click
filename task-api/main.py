from flask import Flask
from pkg.logger.log import init_logger

app = Flask("task-api")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)