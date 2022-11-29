.PHONY: run test-integration

run:
	uvicorn app.main:app --port 7000 --reload --reload-dir app

test:  # run the test on the host machine. Usually we can just use this
	cp .env.test .env
	PYTHONPATH="." pytest -s -v tests/

docker-test:  # run test inside a docker, which is going to be very similar to the CI test
	docker build --target test -t datastore-api-test .
	docker run -v /var/run/docker.sock:/var/run/docker.sock -it datastore-api-test /bin/bash -c "PYTHONPATH=\".\" pytest -s -v tests/"
