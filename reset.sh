# Restore everything back:
if [ -f "./docker-compose.yaml" ]; then
	docker-compose down
fi
rm .env ./**/.env
for docker_volume in "square-core_traefik-public-certificates" "square-core_model_configs" "square-core_onnx_models" "square-core_mongo-data" "square-core_db-data" "square-core_datastore-api-es" "square-core_mongo-dumps" "square-core_square-redis-data"
do
	docker volume rm $docker_volume
done

# Set mode to local:
sed -i -e "s/environment: prod/environment: local/g" ./config.yaml

# Generate local-deployment key
mkdir -p local_deploy
export SQUARE_PRIVATE_KEY_FILE="${PWD}/local_deploy/private_key.pem"
square_pk

# Set init client secrets:
sed -e "s/%%CLIENT_SECRET%%/skill-manager/g" skill-manager/.env.template > skill-manager/.env
sed -e "s/%%CLIENT_SECRET%%/models/g" square-model-inference-api/management_server/.env.template > square-model-inference-api/management_server/.env
sed -e "s/%%CLIENT_SECRET%%/datastores/g" datastore-api/.env.template > datastore-api/.env

# Install ytt:
if [ ! -f "local-bin/ytt" ]; then
	mkdir local-bin/
	curl -L https://carvel.dev/install.sh | K14SIO_INSTALL_BIN_DIR=local-bin bash
fi
export PATH=$PWD/local-bin/:$PATH
ytt version