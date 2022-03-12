from celery import Celery
import logging
import os

logger = logging.getLogger(__name__)

user = os.getenv("USERNAME", "user")
password = os.getenv("PASSWORD", "user")

app = Celery('tasks',
             backend="redis://redishost",
             broker=f"amqp://{user}:{password}@rabbit:5672//",
             include=['tasks.tasks'])

logger.info(password)
logger.info(f"amqp://{user}:{password}@rabbit:5672//")

if __name__ == '__main__':
    app.start()
