from celery import Celery

app = Celery(
    'test_celery_project',
    broker = 'amqp://guest:guest@localhost:5672',
    backend = 'redis://localhost/0',
    include=['checklist_tasks']
)

