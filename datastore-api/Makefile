.PHONY: wait-vespa-config wait-vespa-app run demo-init

wait-vespa-config:
	python scripts/run.py wait-vespa-config

wait-vespa-app:
	python scripts/run.py wait-vespa-app

run:
	python scripts/run.py run

demo-init: wait-vespa-config
	python init_app.py
