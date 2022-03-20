from celery import Celery
import logging
import os

logger = logging.getLogger(__name__)

# use env vars
user = os.getenv("USERNAME", "user")
password = os.getenv("PASSWORD", "user")


app = Celery('tasks',
             backend='rpc://',
             broker=f"amqp://{user}:{password}@rabbit:5672//",
             include=['tasks.tasks'])

if __name__ == '__main__':
    app.start()
