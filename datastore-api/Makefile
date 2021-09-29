.PHONY: wait-vespa-config wait-vespa-app run demo-init test

wait-vespa-config:
	python scripts/run.py wait-vespa config

wait-vespa-app:
	python scripts/run.py wait-vespa app

run:
	python scripts/run.py run --dev

demo-init: wait-vespa-config
	python init_app.py

test: wait-vespa-config
	PYTHONPATH="." python -m pytest -s -v tests/
