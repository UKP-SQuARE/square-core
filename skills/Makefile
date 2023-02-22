.DEFAULT_GOAL := help

##		Install dependencies.
install:
	pip install -r requirements.txt

##		Install dependencies for development.
install-dev:
	pip install -r requirements.dev.txt
	pre-commit install

format:
	black .
	isort --profile black .

SKILL := $(if $(skill),$(skill),local)
##			Run Skill. Provide skill=<skill_name> to run a specific skill. Default is local.
run:
	echo $(SKILL)
	mkdir -p tmp
	cp main.py ./tmp
	cp -r $(SKILL)/. ./tmp/
	cd ./tmp && pwd && bash -c "SQUARE_PRIVATE_KEY_FILE=private_key.pem uvicorn main:app;rm -rf ../tmp"

##			Setup authentication for local development.
auth:
	@square_pk
	@square_token

##		Generate and print an access token from the private key.
token:
	@square_token

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

##			Show this help.	
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^##(.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
