import logging
import os

from celery import Celery

from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)

# initialize env vars
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "ukp")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "secret")

redis_user = os.getenv("REDIS_USER", "default")
redis_password = os.getenv("REDIS_PASSWORD", "secret")

app = Celery(
    "tasks",
    backend=f"redis://{redis_user}:{redis_password}@localhost:6379",
    broker=f"amqp://{rabbitmq_user}:{rabbitmq_password}@localhost:5672//",
    include=["tasks.tasks"],
)

if __name__ == "__main__":
    # app.start()
    worker = app.Worker(
        include=['tasks.tasks']
    )
    worker.start()
