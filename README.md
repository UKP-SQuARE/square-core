# SQuARE
## Local Setup
### dotenv setup
Create `.env` files for each skill, e.g. under `skills/qa-boolq-skill/.env` with the following content:
```
MODEL_API_KEY=your-api-key-goes-here
MODEL_API_URL=http://model_nginx:8080/api
DATA_API_URL=http://host.docker.internal:8002/datastores
```
When running the project locally, provide any api key e.g. `1234-abcd-5678-efgh`.

Next, create an `.env` file for the auth_server under `square-model-inference-api/auth_server/.env` with the following content:
```
MODEL_API_KEY=your-api-key-goes-here
API_KEY_HEADER_NAME=Authorization
```
Make sure the two api keys match.

## Build & Run
Build the project with docker compose by running
```
docker compose build
```
Alternatively, the services can also be build individually by running `docker build .` in the respective folder. Please note that they should also be tagged respectively.
And finally run it
```
docker compose up -d
```

## Register Skills
In the UI register a new user and add skills. The URL for the skill must be the docker internal address. For example, for the boolq skill it would be `http://boolq_skill:8003`. The url comes from the service name specified in the `docker-compose.yml` file, the port from the docker image and code.

