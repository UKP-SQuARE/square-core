#!/bin/bash

generate_password () {
    if [[ $OSTYPE == 'darwin'* ]]; then
        PASSWORD=$(cat /dev/random | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
    else
        PASSWORD=$(cat /dev/urandom | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
    fi

    echo $PASSWORD
}

MONGO_PASSWORD=$(generate_password)
POSTGRES_PASSWORD=$(generate_password)
KEYCLOAK_PASSWORD=$(generate_password)

sed -e "s/%%MONGO_PASSWORD%%/$MONGO_PASSWORD/g" ./skill-manager/.env.example > ./skill-manager/.env 
sed -e "s/%%KEYCLOAK_PASSWORD%%/$KEYCLOAK_PASSWORD/g" -e "s/%%POSTGRES_PASSWORD%%/$POSTGRES_PASSWORD/g" ./keycloak/.env.example > ./keycloak/.env 
sed -e "s/%%POSTGRES_PASSWORD%%/$POSTGRES_PASSWORD/g" ./postgres/.env.example > ./postgres/.env 

for SKILL_DIR in ./skills/*; do
    if [[ -d $SKILL_DIR ]]; then
        cp ./skills/.env.example "$SKILL_DIR/.env"
    fi
done

cp ./square-model-inference-api/management_server/.env.example ./square-model-inference-api/management_server/.env 
cp ./datastore-api/.env.example ./datastore-api/.env 

cp square-frontend/.env.production square-frontend/.env.production-backup
cp square-frontend/.env.development square-frontend/.env.production

