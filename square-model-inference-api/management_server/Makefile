SHELL := /bin/bash

# files to check for linting
SRC=$(shell find . -type f -name '*.py')

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
