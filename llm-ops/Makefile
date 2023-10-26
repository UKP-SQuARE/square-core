SHELL := /bin/bash

# files to check for linting
SRC=$(shell find . -type f -name '*.py')
DOCKER_CONTAINER_LIST := $(shell docker ps -q)

# files to check for quality
check_dirs := .

# global defs
.PHONY: quality lint

quality:
	isort --check ${check_dirs}
	black --check ${check_dirs}
	flake8 ${check_dirs}

lint: $(SRC)
	pylint $? --max-line-length=120


upload:
	docker build -t llm_chat .
	docker tag llm_chat ukpsquare/model-inference-llm:latest
	docker push ukpsquare/model-inference-llm:latest


build:
	docker compose up --detach --build --force-recreate


clean:
	docker compose down
	if [ -n "$(DOCKER_CONTAINER_LIST)" ]; \
	then \
		docker stop "$(DOCKER_CONTAINER_LIST)"; \
	fi
	docker volume rm llm-ops_mongo-data
