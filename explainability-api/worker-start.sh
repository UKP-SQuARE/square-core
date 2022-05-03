#! /usr/bin/env bash
set -e

export $(grep -v '^#' .env | xargs)
python tasks/celeryworker_pre_start.py

#celery worker -A tasks/tasks -l info -Q main-queue -c 1
celery -A tasks.tasks worker --loglevel=info
