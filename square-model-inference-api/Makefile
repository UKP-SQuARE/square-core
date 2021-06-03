SHELL := /bin/bash

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy down

all: clean test install run deploy down

test:
	python -m pip install --upgrade pip && pip install setuptools tox
	tox

install:
	pip install --upgrade pip && pip install -r inference_server/requirements.txt

run:
	PYTHONPATH=inference_server/ uvicorn inference_server.main:app --reload --host 0.0.0.0 --port 8002 --env-file inference_server/.env.debug

build:
	docker-compose build

deploy:
	docker-compose build
	docker-compose up -d

down:
	docker-compose down

clean:
	-find . -name '*.pyc' -exec rm -rf {} \;
	-find . -name '__pycache__' -exec rm -rf {} \;
	-find . -name 'Thumbs.db' -exec rm -rf {} \;
	-find . -name '*~' -exec rm -rf {} \;
	-rm -rf .cache
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -rf htmlcov*
	-rm -rf .tox/
	-rm -rf docs/_build
	-rm -r .coverage
	-rm -rf .pytest_cache