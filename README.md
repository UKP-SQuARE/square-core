# SQuARE: Software for Question Answering Research
## Local Setup
### dotenv setup
Create `.env` files for each skill, e.g. under `skills/qa-boolq-skill/.env` with the following content:
```bash
MODEL_API_KEY=your-api-key-goes-here
MODEL_API_URL=http://model_nginx:8080/api
DATA_API_URL=http://host.docker.internal:8002/datastores
```
When running the project locally, provide any api key e.g. `1234-abcd-5678-efgh`.

Next, create an `.env` file for the auth_server under `square-model-inference-api/auth_server/.env` with the following content:
```bash
MODEL_API_KEY=your-api-key-goes-here
API_KEY_HEADER_NAME=Authorization
```
Make sure the two api keys match.

## Build & Run
For local development it's best to build the project with docker compose by running `docker compose build`.  
If you just want to use the current system, you can pull all images from docker hub with `docker compose pull`.  
And finally run `docker compose up -d` to start the system.  

## Register Skills
In the UI register a new user (if you do not have an account yet) and add skills. The URL for the skill must be the docker internal address. For example, for the boolq skill it would be `http://boolq_skill:8003`. The url comes from the service name specified in the `docker-compose.yml` file, the port from the docker image and code.

