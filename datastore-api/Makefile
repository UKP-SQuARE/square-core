.PHONY: run test-integration

run:
	uvicorn app.main:app --port 7000 --reload --reload-dir app

test-integration:
	PYTHONPATH="." python -m pytest -s -v tests/test_integration/
