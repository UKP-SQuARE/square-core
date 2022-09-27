SHELL := /bin/bash

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy clean-deploy down

all: clean test install run deploy down

test:
	python -m pip install --upgrade pip && pip install pytest pytest-cov pytest-asyncio
	PYTHONPATH=inference_server/ pytest inference_server/  --cov
	PYTHONPATH=../model-manager/ pytest ../model-manager/  --cov
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