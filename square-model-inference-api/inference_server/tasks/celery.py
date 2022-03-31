import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

# use env vars
user = os.getenv("USERNAME", "user")
password = os.getenv("PASSWORD", "user")

app = Celery('tasks',
             backend='rpc://',
             broker=f"amqp://{user}:{password}@rabbit:5672//",
             include=['tasks.tasks'])
# app.conf.task_routes = {
#     'tasks.add': {'queue': 'dpr'},
#     'tasks.predict': {'queue': 'dpr'}
# }

if __name__ == '__main__':
    app.start()
