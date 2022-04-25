from .celery_app import app
from .utils import run_tests

import json


@app.task(name='run_checklist')
def run_checklist(data):

    json_data = run_tests(data)

    return json_data


