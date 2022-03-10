#!/bin/bash
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

SQUARE_URL=${1:-"square.ukp-lab.local"}
REALM=${2:-"square"}
KEYCLOAK_PASSWORD=${3:-$(generate_password)}
POSTGRES_PASSWORD=${4:-$(generate_password)}
MONGO_PASSWORD=${5:-$(generate_password)}

keycloak_get_admin_token () {
	# returns an admin token from the master realm
	RESPONSE=$(curl -s -k -L --fail-with-body -X POST \
		"https://$SQUARE_URL/auth/realms/master/protocol/openid-connect/token/" \
		-H 'Content-Type: application/x-www-form-urlencoded' \
		--data-urlencode "grant_type=password" \
		--data-urlencode "client_id=admin-cli" \
		--data-urlencode "username=admin" \
		--data-urlencode "password=$KEYCLOAK_PASSWORD"
	)
	ADMIN_TOKEN=$(echo $RESPONSE |  jq -r '.access_token')

	echo $ADMIN_TOKEN
}

keycloak_create_realm () {
	# creates a new realm in keycloak
	ADMIN_TOKEN=$(keycloak_get_admin_token)
	PAYLOAD=$(cat <<- EOF
		{
			"realm": "$REALM", 
			"enabled": true
		}
		EOF
	)
	curl -s -k -L --fail-with-body -o /dev/null -X POST \
		"https://$SQUARE_URL/auth/admin/realms" \
		-H "Authorization: Bearer $ADMIN_TOKEN" \
		-H 'Content-Type: application/json' \
		--data-raw "$PAYLOAD"
}

keycloak_get_initial_access_token () {
	# gets a new initial access token for a realm that can be used once

	RESPONSE=$(curl -s -k -L --fail-with-body -X POST \
		"https://$SQUARE_URL/auth/admin/realms/$REALM/clients-initial-access" \
		-H "Authorization: Bearer $ADMIN_TOKEN" \
		-H 'Content-Type: application/json' \
		--data-raw '{ "count": 1, "expiration": 60 }'
	)
	INITIAL_ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.token')
	
	echo $INITIAL_ACCESS_TOKEN
}

keycloak_get_client_token () {
	# returns an access token obtained by the client credentials flow
	CLIENT_ID=$1
	CLIENT_SECRET=$2
	RESPONSE=$(curl -s -k -L --fail-with-body -X POST \
		"https://$SQUARE_URL/auth/realms/$REALM/protocol/openid-connect/token" \
		-H 'Content-Type: application/x-www-form-urlencoded' \
		--data-urlencode 'grant_type=client_credentials' \
		--data-urlencode "client_id=$CLIENT_ID" \
		--data-urlencode "client_secret=$CLIENT_SECRET"
	)
	CLIENT_TOKEN=$(echo $RESPONSE | jq -r '.access_token')

	echo $CLIENT_TOKEN
}

keycloak_create_client_registration_client () {
	# creates the a client that is able to create new clients
	INITIAL_ACCESS_TOKEN=$(keycloak_get_initial_access_token)
	SECRET=$(generate_password)
	PAYLOAD=$(cat <<- EOF
		{
			"clientId": "skill-manager",
			"secret": "$SECRET",
			"implicitFlowEnabled": false,
			"standardFlowEnabled": false,
			"serviceAccountsEnabled": true,
			"publicClient": false
		}
		EOF
	)

	# ===== Create the `skill-manager` client =====
	RESPONSE=$(curl -s -k -L --fail-with-body -X POST \
		"https://$SQUARE_URL/auth/realms/$REALM/clients-registrations/default" \
		-H "Authorization: Bearer $INITIAL_ACCESS_TOKEN" \
		-H 'Content-Type: application/json' \
		--data-raw "$PAYLOAD"
	)
	SKILL_MANAGER_ID=$(echo $RESPONSE | jq -r ".id")
	
	# return skill-manager client secret
	echo $SECRET
	
	ADMIN_TOKEN=$(keycloak_get_admin_token)

	# ===== Get the ID of the `realm-management` user =====
	RESPONSE=$(curl -s -k -L --fail-with-body -X GET \
		"https://$SQUARE_URL/auth/admin/realms/$REALM/clients?clientId=realm-management&max=20&search=true" \
		-H "Authorization: Bearer $ADMIN_TOKEN"
	)
	REALM_MANAGEMENT_ID=$(echo $RESPONSE | jq -r '.[0].id')

	# ===== Get the ID of the service account of the skill-manager =====
	RESPONSE=$(curl -s -k -L --fail-with-body -X GET \
		"https://$SQUARE_URL/auth/admin/realms/$REALM/clients/$SKILL_MANAGER_ID/service-account-user" \
		-H "Authorization: Bearer $ADMIN_TOKEN"
	)
	SERVICE_ACCOUNT_ID=$(echo $RESPONSE | jq -r '.id')

	# ===== Get the `create-client` role id of the realm-management client for the service account  =====
	RESPONSE=$(curl -s -k -L --fail-with-body -X GET \
	"https://$SQUARE_URL/auth/admin/realms/$REALM/users/$SERVICE_ACCOUNT_ID/role-mappings/clients/$REALM_MANAGEMENT_ID/available" \
	-H "Authorization: Bearer $ADMIN_TOKEN")
	CREATE_CLIENT_ID=$(echo $RESPONSE | jq -r '.[] | select(.name | contains("create-client")) | .id')

	PAYLOAD=$(cat <<- EOF
		[
			{
				"id": "$CREATE_CLIENT_ID",
				"name": "create-client",
				"description": "${role_create-client}",
				"composite": false,
				"clientRole": true,
				"containerId": "$REALM_MANAGEMENT_ID"
			}
		] 
		EOF
	)

	# ===== Assign the service account the `create-client` role from the realm-management  =====
	curl -s -k -L --fail-with-body -o /dev/null -X POST \
	"https://$SQUARE_URL/auth/admin/realms/$REALM/users/$SERVICE_ACCOUNT_ID/role-mappings/clients/$REALM_MANAGEMENT_ID" \
	-H "Authorization: Bearer $ADMIN_TOKEN" \
	-H 'Content-Type: application/json' \
	--data-raw "$PAYLOAD"

}

keycloak_create_client () {
	# create any client for clients credentials flow
	# these clients are used for machine to machine authentication
	CLIENT_ID=$1
	SKILL_MANAGER_SECRET=$2
	TOKEN=$(keycloak_get_client_token "skill-manager" $SKILL_MANAGER_SECRET)
	SECRET=$(generate_password)
	echo $SECRET

	PAYLOAD=$(cat <<- EOF
		{
			"clientId": "$CLIENT_ID",
			"secret": "$SECRET",
			"implicitFlowEnabled": false,
			"standardFlowEnabled": false,
			"serviceAccountsEnabled": true,
			"publicClient": false
		}
		EOF
	)

	curl -s -k -L --fail-with-body -o /dev/null -g -X POST \
	"https://$SQUARE_URL/auth/realms/$REALM/clients-registrations/default" \
	-H "Authorization: Bearer $TOKEN" \
	-H "Content-Type: application/json" \
	--data-raw "$PAYLOAD"

}

keycloak_create_frontend_client () {
	# creates client for the frontend
	SKILL_MANAGER_SECRET=$1
	TOKEN=$(keycloak_get_client_token "skill-manager" $SKILL_MANAGER_SECRET)

	PAYLOAD=$(cat <<- EOF
		{
			"clientId": "web-app",
			"redirectUris": ["https://$SQUARE_URL"],
			"webOrigins": ["+"],
			"implicitFlowEnabled": false,
			"standardFlowEnabled": true,
			"serviceAccountsEnabled": false,
			"publicClient": true,
			"fullScopeAllowed": false
		}
		EOF
	)

	curl -s -k -L --fail-with-body -o /dev/null -g -X POST \
	"https://$SQUARE_URL/auth/realms/$REALM/clients-registrations/default" \
	-H "Authorization: Bearer $TOKEN" \
	-H "Content-Type: application/json" \
	--data-raw "$PAYLOAD"
}

# replace passwords in env files
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
CLIENTS=( "models" "datastores" ) 
cd ./skills
for SKILL_DIR in ./*; do
	if [[ -d $SKILL_DIR ]]; then
		cp ./.env.example "$SKILL_DIR/.env"
		SKILL=$(echo "$SKILL_DIR" | sed -e "s/\.\///")
		CLIENTS+=( "$SKILL" )
	fi
done
cd ..

# bring up services required to setup authentication
ytt -f docker-compose.ytt.yaml -f config.yaml >> docker-compose.yaml
sleep 1
docker-compose pull
docker-compose up -d traefik db keycloak

echo "Setting up Authorizaton."
while [ $(curl -s -k -L -o /dev/null -w "%{http_code}" "https://$SQUARE_URL/auth") -ne "200" ]; do
	echo "Waiting for Keycloak to be ready."
	sleep 3
done

keycloak_create_realm

# create the skill-manager client that is able to create other clients
SKILL_MANAGER_SECRET=$(keycloak_create_client_registration_client)
echo "SKILL_MANAGER_SECRET=$SKILL_MANAGER_SECRET"
sed -e "s/%%CLIENT_SECRET%%/$SKILL_MANAGER_SECRET/g" ./skill-manager/.env > ./skill-manager/.env.tmp
mv ./skill-manager/.env.tmp ./skill-manager/.env

# create clients in keycloak and save client secret
for CLIENT_ID in ${CLIENTS[@]}; do
	CLIENT_SECRET=$(keycloak_create_client $CLIENT_ID $SKILL_MANAGER_SECRET)
	echo "CLIENT_ID=$CLIENT_ID CLIENT_SECRET=$CLIENT_SECRET"
	
	if [[ $CLIENT_ID == "models" ]]; then
		CLIENT_PATH="square-model-inference-api/management_server"
	
	elif [[ $CLIENT_ID == "datastores" ]]; then
		CLIENT_PATH="datastore-api"
	
	else
		CLIENT_PATH="skills/$CLIENT_ID"
	fi
	
	sed -e "s/%%CLIENT_SECRET%%/$CLIENT_SECRET/g" ./$CLIENT_PATH/.env > ./$CLIENT_PATH/.env.tmp
	mv ./$CLIENT_PATH/.env.tmp ./$CLIENT_PATH/.env
done

keycloak_create_frontend_client $SKILL_MANAGER_SECRET

docker-compose down
echo "Authorization setup complete."

# build frontend with updated env file
cp square-frontend/.env.production square-frontend/.env.production-backup
cp square-frontend/.env.development square-frontend/.env.production

docker-compose build frontend
