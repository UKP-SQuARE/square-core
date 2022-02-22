# Skill-Manager
The Skill-Manager serves as a central service for interacting with the Skills. It provides a RESTful CRUD (Create, Read, Update, Delete) interface for Skills. All skill information is saved in a [mongoDB](https://www.mongodb.com/) instance. Further, it allows interacting with skills by checking their health, querying them, and changing their public/private status.

## Project Structure
```
├───skill_manager
│   ├───mongo
│   │   ├───mongo_client.py         # wrapper class for (dis-)connecting to mongoDB
│   │   ├───mongo_model.py          # utility interface for loading data from and to mongoDB
│   │   ├───py_object_id.py         # utility class for mongoDB ID
│   ├───settings
│   │   ├───keycloak_settings.py    # Settings class for Keycloak, loads .env variables
│   │   ├───mongo_settings.py       # Settings class for MongoDB, loads .env variables
│   ├───routers
│   │   ├───api.py                  # main router for all routes with `/api` prefix
│   │   ├───health.py               # routes with `/api/health` prefix
│   │   ├───skill_types.py          # routes with `/api/skill-types` prefix
│   │   ├───skill.py                # routes with `/api/skill` prefix
│   ├───keycloak_api.py             # Class for managaing Clients in Keycloak
│   ├───main.py                     # main file creatng the `app` object
│   ├───models.py                   # input and output of endpoints
├───tests
│   ├───test_api.py
├───.env                            # environment file loaded by root docker-compose.yaml
├───Dockerfile                      # image definition
├───logging.conf                    # logging configuration
├───requirements.dev.txt            # dependencies for development
├───requirements.txt                # dependencies
```

## Testing
Tests include integration tests with mongoDB. To run them successfully docker needs to be installed and running on your system. The test will automatically spin up a mongoDB instance for testing and shut it down at the end of testing.
```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
python -m pytest
```
## Setup
### Environment Configuration
The `.env` file holds the access information to the mongoDB. We recommend running mongoDB through docker.  
The access information for MongoDB has to be configured when starting the service via docker. For example:  
```bash
docker run -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=example mongo
```
In this case, mongoDB will be running on the `localhost` on port `27017`. The root username will be `root`, and the password `example`. For details see the docker hub [mongo](https://hub.docker.com/_/mongo) image description.  
Set the same configuration in the `.env`. For example:
```bash
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
MONGO_HOST=localhost
MONGO_PORT=27017
KEYCLOAK_SKILL_MANAGER_CLIENT_SECRET=PASTE_FROM_NEXT_STEP
```
### Keycloak Skill-Manager Client Setup
When new skills are created, the skill-manager also creates new clients in Keycloak. For this, the skill-manager requires the privilages to create clients.
1. Login to the admin console of keycloak
2. Select the realm where the skill-manager should create clients
3. Create a new client with client id `skill-manager` (or any other client id, but then it needs to be set as the `KEYCLOAK_SKILL_MANAGER_CLIENT_ID` env variable)
4. In the Settings tab
    - set the Access Type to `confidential`
    - disable Standard Flow Enabled and Direct Access Grants Enabled
    - enable Service Accounts Enabled
    - save
5. In the Service Account Roles tab under at Client Roles, select `realm-management` and add the `create-client` and `manage-client` to the assigned roles
6. In the Credentials tab copy the secret and set it in the .env file
