SHELL := /bin/bash

PYTHON=3.10
BASENAME=model-api
CONDA_CH=conda-forge defaults

# files to check for linting
SRC=$(shell find . -type f -name '*.py')

# files to check for quality
check_dirs := ./inference_api

# envs
ifneq (,$(wildcard ./.env.test))
    include .env.test
    export
endif

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy clean-deploy down quality lint reformat

all: clean test install run deploy down

# PRE-REQUISITES

env:
	conda create -n $(BASENAME)  python=$(PYTHON)

quality:
	isort --check ${check_dirs}
	black --check ${check_dirs}
	flake8 ${check_dirs}

lint: $(check_dirs)
	pylint $? --max-line-length=120

reformat:
	black -l 120 ${SRC}
	isort -r ${SRC}

test:
	python -m pip install --upgrade pip && pip install pytest pytest-cov pytest-asyncio
	PYTHONPATH=inference_api/ pytest inference_api/  --cov

full-test:
	python -m pip install --upgrade pip && pip install pytest pytest-cov pytest-asyncio
	PYTHONPATH=inference_server/ pytest inference_server/  --cov
	PYTHONPATH=../model-manager/ pytest ../model-manager/  --cov

install:
	pip install --upgrade pip
	pip install -r inference_api/dockerfiles/base_model/requirements.txt
	pip install -r inference_api/dockerfiles/transformer/requirements.txt


## RUN ON LOCAL MACHINE

app:
	export QUEUE="bert-base-uncased" && \
	PYTHONPATH=inference_api/ uvicorn inference_api.main:app --reload --host 0.0.0.0 --port 8000 --env-file inference_api/model_configs/.env.bert_adapter

redis:
	docker build -t redis -f inference_api/dockerfiles/redis/Dockerfile .
	docker run -d -p 6379:6379 --name redis redis

rabbitmq:
	docker build -t rabbit -f inference_api/dockerfiles/rabbitmq/Dockerfile .
	docker run -d -p 5672:5672 --name rabbit rabbit

worker:
	#$(call setup_env, inference_api/.env.test)
	export QUEUE="bert-base-uncased" && \
	PYTHONPATH=inference_api/ celery -A tasks worker -Q QUEUE --loglevel=info --concurrency=1


## RUNNING ON DOCKER

build:
	docker-compose build

deploy:
	docker-compose build
	docker-compose up -d

clean-deploy:
	docker-compose down
	docker rm -f $(docker ps -a -q)
	docker volume rm $(docker volume ls -q)
	docker-compose up

down:
	docker-compose down

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