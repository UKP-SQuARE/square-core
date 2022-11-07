SHELL := /bin/bash

# files to check for linting
SRC=$(shell find . -type f -name '*.py')

# files to check for quality
check_dirs := ./inference_api

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy clean-deploy down quality lint reformat

all: clean test install run deploy down

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
	#PYTHONPATH=../model-manager/ pytest ../model-manager/  --cov
# 	PYTHONPATH=management_server/ pytest management_server/  --cov

full-test:
	python -m pip install --upgrade pip && pip install pytest pytest-cov pytest-asyncio
	PYTHONPATH=inference_server/ pytest inference_server/  --cov
	PYTHONPATH=../model-manager/ pytest ../model-manager/  --cov
# 	PYTHONPATH=management_server/ pytest management_server/  --cov
	PYTHONPATH=management_client/ pytest management_client/  --cov

install:
	pip install --upgrade pip
	pip install -r inference_server/requirements1.txt
	pip uninstall -y -r inference_server/uninstall_requirements.txt
	pip install -r inference_server/requirements2.txt

run:
	export CONFIG_PATH="./.test_configs"  && \
	PYTHONPATH=inference_server/ uvicorn inference_server.main:app --reload --host 0.0.0.0 --port 8000 --env-file inference_server/.env.bert_adapter

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