docker-compose:
	if [ -f docker-compose.yaml ]; then \
		rm -f docker-compose.yaml; \
	fi
	ytt -f docker-compose.ytt.yaml -f config.yaml > docker-compose.yaml
