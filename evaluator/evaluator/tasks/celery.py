import logging
import os

from celery import Celery

from evaluator.app.settings.redis_settings import RedisSettings

logger = logging.getLogger(__name__)

# initialize env vars
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "ukp")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "secret")
redis_settings = RedisSettings()


app = Celery(
    "evaluator.tasks",
    backend=f"redis://{redis_settings.username}:{redis_settings.password}@{redis_settings.host}:6379",
    broker=f"amqp://{rabbitmq_user}:{rabbitmq_password}@rabbit:5672//",
    include=[
        "evaluator.tasks.predict_task",
        "evaluator.tasks.evaluate_task",
    ],
    result_extended=True,
)

if __name__ == "__main__":
    app.start()
