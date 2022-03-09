from celery import Celery
import logging

logger = logging.getLogger(__name__)

# use env vars
app = Celery('tasks',
             backend='rpc://',
             broker="amqp://guest:guest@rabbit:5672//",
             include=['tasks.tasks'])

if __name__ == '__main__':
    app.start()
