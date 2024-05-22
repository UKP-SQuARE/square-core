up:
	docker compose up --remove-orphans --detach --build --force-recreate

stop:
	docker compose down
	if [ -n "$(DOCKER_CONTAINER_LIST)" ]; \
	then \
		docker stop "$(DOCKER_CONTAINER_LIST)" || true ; \
	fi
