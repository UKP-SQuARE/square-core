.PHONY: run test-integration

run:
	uvicorn app.main:app --port 7000 --reload --reload-dir app

test:
	PYTHONPATH="." python -m pytest -s -v tests/

test-api:
	cp .env.test .env
	PYTHONPATH="." MOCK_DEPENDENCIES=1 pytest -s -v tests/
