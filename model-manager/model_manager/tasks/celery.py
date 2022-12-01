import logging
import os

from celery import Celery


logger = logging.getLogger(__name__)

# initialize env vars
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "ukp")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "secret")

redis_user = os.getenv("REDIS_USER", "ukp")
redis_password = os.getenv("REDIS_PASSWORD", "secret")
redis_host = os.getenv("REDIS_HOST", "redis")

app = Celery(
    "tasks",
    backend=f"redis://{redis_user}:{redis_password}@{redis_host}:6379",
    broker=f"amqp://{rabbitmq_user}:{rabbitmq_password}@rabbit:5672//",
    include=["model_manager.tasks.tasks"],
    result_extended=True
)

if __name__ == "__main__":
    app.start()
