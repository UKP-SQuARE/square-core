SHELL := /bin/bash

# global defs
.PHONY: run-checks

run-checks:
	isort --check .
	black --check .
	flake8 .
