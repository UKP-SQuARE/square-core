# Restore everything back:
if [ -f "./docker-compose.yaml" ]; then
	docker-compose down
fi
rm .env ./**/.env
docker volume prune -f

# Set mode to local:
sed -i -e "s/environment: prod/environment: local/g" ./config.yaml

# Set init client secrets:
sed -e "s/%%CLIENT_SECRET%%/skill-manager/g" skill-manager/.env.template > skill-manager/.env
# sed -e "s/%%CLIENT_SECRET%%/models/g" square-model-inference-api/management_server/.env.template > square-model-inference-api/management_server/.env
sed -e "s/%%CLIENT_SECRET%%/datastores/g" datastore-api/.env.template > datastore-api/.env

# Install ytt:
if [ ! -f "local-bin/ytt" ]; then
	mkdir local-bin/
	curl -L https://carvel.dev/install.sh | K14SIO_INSTALL_BIN_DIR=local-bin bash
fi
export PATH=$PWD/local-bin/:$PATH
ytt version