# Get Started


## Local Setup

### Prerequisites

- Python 3.7+
- Install <b>docker</b> and <b>docker-compose</b>
- <b>dotenv setup</b> <br>
Clone Square repository from github
`git clone https://github.com/UKP-SQuARE/square-core.git` and create `.env` files for each skill, e.g. under `skills/qa-boolq-skill/.env` with the following content:
```bash
MODEL_API_KEY=your-api-key-goes-here
MODEL_API_URL=http://model_nginx:8080/api
DATA_API_URL=http://host.docker.internal:8002/datastores
```
When running the project locally, provide any api key e.g. `1234-abcd-5678-efgh`.

Next, create your user and password with `htpasswd` and add it under `square-model-inference-api/traefik/traefik.yaml`.

### Build & Run
- Build the project using `docker compose build`.  
- If you just want to use the latest system, you can pull all images from docker hub with `docker compose pull`.  
And finally run `docker compose up -d` to start the system.  

## Using the Platform

> **_NOTE:_**  Visit the SQuARE [website](http://square.ukp.informatik.tu-darmstadt.de/#/).

### Registering Skills

- In the UI, register a new user (if you do not have an account yet).
- Add skills. The URL for the skill must be the docker internal address. For example, 
for the boolq skill it would be `http://boolq_skill:8003`. The url comes from the service name 
specified in the `docker-compose.yml` file, the port from the docker image and code.
- Use the created skill to get predictions for your input queries.
