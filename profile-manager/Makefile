.DEFAULT_GOAL := help

##		Install dependencies.
install:
	pip install --upgrade pip
	pip install -r requirements.txt

##		Install dependencies for development.
install-dev:
	pip install --upgrade pip
	pip install -r requirements.dev.txt
	pre-commit install

##		Format code base. Run before commiting.
format:
	black .
	isort --profile black --filter-files profile_manager
	isort --profile black --filter-files tests


##			Setup authentication for local development.
auth:
	@square_pk
	@square_token

##		Generate and print an access token from the private key.
token:
	@square_token

##			Bring up the development environment.
up:
	docker compose --env-file .local.env up -d 
##			Bring down the development environment.
down:
	docker compose --env-file .local.env down
##		Build the development environment.
build:
	docker compose --env-file .local.env build 
##			Show logs from the development environment.
logs:
	docker compose --env-file .local.env logs -f profile-manager


# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
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
