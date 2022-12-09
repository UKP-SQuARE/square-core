# Restore everything back:
if [ -f "./docker-compose.yaml" ]; then
	docker-compose down -v
fi
rm .env ./**/.env

# Generate local-deployment key
mkdir -p local_deploy
export SQUARE_PRIVATE_KEY_FILE="${PWD}/local_deploy/private_key.pem"
square_pk

# Install ytt:
if [ ! -f "local-bin/ytt" ]; then
	mkdir local-bin/
	curl -L https://carvel.dev/install.sh | K14SIO_INSTALL_BIN_DIR=local-bin bash
fi
export PATH=$PWD/local-bin/:$PATH
ytt version
