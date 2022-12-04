import time

from .celery import app as celery_app


@celery_app.task
def test_something():
    time.sleep(15)
    return "This is the result of the test task"
