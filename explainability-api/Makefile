SHELL := /bin/bash

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy down

all: clean test install run-backend run-celery deploy down

test:
	python -m pip install --upgrade pip && pip install pytest pytest-cov pytest-asyncio
	PYTHONPATH=./ pytest ./  --cov

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-backend:
	PYTHONPATH=app/ uvicorn main:app --reload --host 0.0.0.0 --port 8010 --env-file .env

run-celery:
	PYTHONPATH=./ bash worker-start.sh

build:
	docker-compose -f docker-compose.dev.yaml build

deploy:
	docker-compose -f docker-compose.dev.yaml build
	docker-compose -f docker-compose.dev.yaml up -d

down:
	docker-compose -f docker-compose.dev.yaml down

clean:
	-find . -name '*.pyc' -exec rm -rf {} \;
	-find . -name '__pycache__' -exec rm -rf {} \;
	-find . -name 'Thumbs.db' -exec rm -rf {} \;
	-find . -name '*~' -exec rm -rf {} \;
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -rf docs/_build
	-rm -rf .pytest_cache