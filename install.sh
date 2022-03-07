#!/bin/bash
set -e

generate_password () {
    if [[ $OSTYPE == 'darwin'* ]]; then
        PASSWORD=$(cat /dev/random | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
    else
        PASSWORD=$(cat /dev/urandom | LC_CTYPE=C tr -dc "[:alpha:]" | head -c 32)
    fi

    echo $PASSWORD
}

SQUARE_URL=${1:-"square.ukp-lab.local"}
KEYCLOAK_PASSWORD=${2:-$(generate_password)}
POSTGRES_PASSWORD=${3:-$(generate_password)}
MONGO_PASSWORD=${4:-$(generate_password)}

keycloak_admin_token () {
    KEYCLOAK_PASSWORD=$1
    # echo "KC PWD= $KEYCLOAK_PASSWORD"
    ACCESS_TOKEN=$(curl -s --insecure --fail-with-body -X POST \
        "https://$SQUARE_URL/auth/realms/master/protocol/openid-connect/token/" \
        -H 'Content-Type: application/x-www-form-urlencoded' \
        --data-urlencode "grant_type=password" \
        --data-urlencode "client_id=admin-cli" \
        --data-urlencode "username=admin" \
        --data-urlencode "password=$KEYCLOAK_PASSWORD" | jq -r '.access_token')
    echo $ACCESS_TOKEN
}

keycloak

create_keycloak_realm () {
    ACCESS_TOKEN=$1
    curl -s --insecure -X POST "https://square.ukp-lab.local/auth/admin/realms" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H 'Content-Type: application/json' \
        --data-raw '{"realm": "square", "enabled": true}'
}


create_keycloak_client () {
    ACCESS_TOKEN=$1
    REALM=$2
    CLIENT_ID=$3
    SECRET=$(generate_password)

    get_client_post_data () {
    cat <<EOF
{
    "clientId": "$CLIENT_ID",
    "secret": "$SECRET",
    "implicitFlowEnabled": false,
    "standardFlowEnabled": false,
    "serviceAccountsEnabled": true,
    "publicClient": false
}
EOF
    }

    curl -v --insecure -g -X POST \
    "https://$SQUARE_URL/auth/realms/$REALM/clients-registrations/default" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    --data-raw "$(get_client_post_data $CLEINT_ID $SECRET)"
    
    echo $SECRET
}

# replace vars in env files
if [ -f ./keycloak/.env ]; then
    echo "./keycloak/.env already exists. Skipping."
else
    sed -e "s/%%KEYCLOAK_PASSWORD%%/$KEYCLOAK_PASSWORD/g" -e "s/%%POSTGRES_PASSWORD%%/$POSTGRES_PASSWORD/g" ./keycloak/.env.example > ./keycloak/.env 
    sed -e "s/%%POSTGRES_PASSWORD%%/$POSTGRES_PASSWORD/g" ./postgres/.env.example > ./postgres/.env 
fi

if [ -f ./skill-manager/.env ]; then
    echo "./skill-manager/.env already exists. Skipping."
else
    sed -e "s/%%MONGO_PASSWORD%%/$MONGO_PASSWORD/g" ./skill-manager/.env.example > ./skill-manager/.env 
fi

# initilize env files for model management service and datastore
cp ./square-model-inference-api/management_server/.env.example ./square-model-inference-api/management_server/.env 
cp ./datastore-api/.env.example ./datastore-api/.env 

# get all servies that need to be registered as clients keycloak
CLIENTS=( "skill-manager" "models" "datastores" )
cd ./skills
for SKILL_DIR in ./*; do
    if [[ -d $SKILL_DIR ]]; then
        cp ./.env.example "$SKILL_DIR/.env"
        SKILL=$(echo $SKILL_DIR | sed -e "s/\.\///")
        CLIENTS+=( "$SKILL" )
    fi
done
cd ..
# echo "${CLIENTS[*]}"

ytt -f docker-compose.ytt.yaml -f config.yaml >> docker-compose.yaml

# sleep 3
# docker-compose up -d traefik db keycloak

echo "Setting up Authorizaton."
while [ $(curl --insecure -L -s -o /dev/null --insecure -w "%{http_code}" https://$SQUARE_URL/auth) -ne "200" ]; do
    echo "Waiting for Keycloak to be ready."

    sleep 3
done

ACCESS_TOKEN=$(keycloak_admin_token $KEYCLOAK_PASSWORD)
# create_keycloak_realm $ACCESS_TOKEN

for CLIENT in ${CLIENTS[@]}; do
    CLIENT_SECRET=$(create_keycloak_client $ACCESS_TOKEN "square" $CLIENT)
    echo "CLIENT=$CLIENT CLIENT_SECRET=$CLIENT_SECRET"
    if [[ $CLIENT == "models" ]]; then
        CLIENT_PATH="square-model-inference-api/management_server"
    elif [[ $CLIENT == "datastores" ]]; then
        CLIENT_PATH="datastore-api"
    elif [[ $CLIENT == "skill-manager" ]]; then
        CLIENT_PATH="skill-manager"
    else
        CLIENT_PATH="skills/$CLIENT"
    fi
    sed -e "s/%%CLIENT_SECRET%%/$CLIENT_SECRET/g" ./$CLIENT_PATH/.env.example > ./$CLIENT_PATH/.env 
done

# docker-compose down

# build frontend with updated env file
cp square-frontend/.env.production square-frontend/.env.production-backup
cp square-frontend/.env.development square-frontend/.env.production

