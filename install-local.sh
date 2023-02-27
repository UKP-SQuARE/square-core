#!/bin/bash
# Restore everything back:
source ./reset.sh

# Begin the usual installation steps: (note that docker-compose.ytt.yaml.min will be used)
set -e

generate_password () {
	# generates a random password with 32 alphanumeric characters
	if [[ $OSTYPE == 'darwin'* ]]; then
		PASSWORD=$(cat /dev/random | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
	else
		PASSWORD=$(cat /dev/urandom | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
	fi

	echo "$PASSWORD"
}

SQUARE_URL=${1:-"square.ukp-lab.localhost"}
MONGO_PASSWORD=${2:-$(generate_password)}
RABBITMQ_PASSWORD=${3:-$(generate_password)}
REDIS_PASSWORD=${4:-$(generate_password)}
SQUARE_ADMIN_PASSWORD=${5:-$(generate_password)}
MODEL_MANAGER_PASSWORD=${6:-$(generate_password)}
SQUARE_ADMIN_PASSWORD_HASHED=$(openssl passwd -apr1 $SQUARE_ADMIN_PASSWORD)
SQUARE_ADMIN_PASSWORD_HASHED_ESCAPED=$(echo "$SQUARE_ADMIN_PASSWORD_HASHED" | sed 's/\//\\\//g')

# replace passwords in env files
if [ -f ./.env ]; then
	echo "./.env already exists. Skipping."
else
	sed -e "s/%%SQUARE_ADMIN_PASSWORD%%/'$SQUARE_ADMIN_PASSWORD_HASHED_ESCAPED'/g; s/%%REDIS_PASSWORD%%/$REDIS_PASSWORD/g" ./.env.template > ./.env
fi

if [ -f ./mongodb/.env ]; then
	echo "./mongodb/.env already exists. Skipping."
	eval "$(grep ^MONGO_INITDB_ROOT_PASSWORD= ./mongodb/.env)"    
else
	sed -e "s/%%MONGO_PASSWORD%%/$MONGO_PASSWORD/g" ./mongodb/.env.template > ./mongodb/.env
fi

if [ -f ./rabbitmq/.env ]; then
	echo "./rabbitmq/.env already exists. Skipping."
	eval "$(grep ^RABBITMQ_DEFAULT_PASS= ./rabbitmq/.env)"    
else
	sed -e "s/%%RABBITMQ_DEFAULT_PASS%%/$RABBITMQ_DEFAULT_PASS/g" ./rabbitmq/.env.template > ./rabbitmq/.env
fi

if [ -f ./redis/.env ]; then
	echo "./redis/.env already exists. Skipping."
	eval "$(grep ^REDIS_PASSWORD= ./redis/.env)"    
else
	sed -e "s/%%REDIS_PASSWORD%%/$REDIS_PASSWORD/g" ./redis/.env.template > ./redis/.env
fi

if [ -f ./model-manager/.env ]; then
	echo "./model-manager/.env already exists. Skipping."
	eval "$(grep ^MODEL_MANAGER_PASSWORD= ./model-manager/.env)"    
else
	sed -e "s/%%MODEL_MANAGER_PASSWORD%%/$MODEL_MANAGER_PASSWORD/g" ./model-manager/.env.template > ./model-manager/.env
fi

# create .env file for Datastores
cp ./datastore-api/.env.template ./datastore-api/.env

# bring up services required to setup authentication
ytt -f docker-compose.ytt.min.yaml -f config.yaml --data-value environment=local > docker-compose.yaml
sleep 1
echo "Pulling Images. This might take a while. Meanwhile grab a coffe c[_]. "
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose pull

E=$(cat <<- EOF
	H4sIAERZKmIAA5VTQQ7DMAi79xU8dYcedlykJpMm7XO8ZKRqBoHUTSUOyCkY2yqX
	J0vlNxFx61lBj9nah0gH4zNEe87w7dV4eFhal8zepGDrNs5f079q9YL861FhygxC
	bs8yizdeqEwdqMKGnhnFxq8zHy9sBBcA/OQGIpza1oUz8kcU54/PySFBBJdVak6d
	T2k6VTlN1Mkp2I1KOvSe8N+V0OpbrAlgIbEl2N2FIJr/rcFUzGDapVgetdyyW2wB
	8wt+SX8/uvYEAAA=
	EOF
)
WELCOME="$(echo "$E" | base64 -d | gunzip)"
echo "$WELCOME"
echo "$(cat <<-EOF
	Congrats! UKP-SQuARE has been sucessfully installed! 
	You can run it with: docker-compose up -d
	Then visit: https://$SQUARE_URL
EOF
)"
