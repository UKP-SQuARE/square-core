# SQuARE Model API
Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## On the API Path
The 'true' path of the API for the model server is of the form `/api/$endpoint` where the endpoint
is embeddings, question-answering, etc. This is the path you use if you just run a model server locally.

However, to run and distinguish multiple models, we use an API gateway with nginx so we extend 
the path to `/api/$modelname/$endpoint` which is then resolved by nginx to the correct model server and forwarded
to this server's `/api/$endpoint` endpoint. This is the path you use with Docker.
This requires you to setup the docker-compose and nginx config as described below.

## Project structure

The Model API uses 3 components: 
1 authorization server, n inference servers (each with their own model), 
and a nginx server that serves as API gateway to forward requests to the correct inference server and
to handle authorization of requests with the auth server.
```
├───auth_server                 # FastAPI Authorization Server
│   ├───main.py                 # Entry point in server
│   ├───Dockerfile              # Dockerfile for server
│   ├───tests                   # Unit Tests
│   │   ├───test_api
│   └───auth_api
├───inference_server            # FastAPI Model API Server
│   ├───tests                   # Unit Tests
│   │   ├───test_api
│   │   ├───test_inference
│   ├───main.py                 # Entry point in server
│   ├───Dockerfile              # Dockerfile for server
│   └───square_model_inference  # Server Logic
│       ├───api                 # API Routes
│       │   ├───routes
│       ├───core                # Server config, Startup logic, etc.
│       ├───models              # Input/ output modelling for API
│       └───inference           # Deep Model implementation and inference code for NLP tasks
├───nginx                       # nginx config for API Gateway & Authorizatio
│   └───nginx.conf
├───locust                      # Load testing configuration with Locust
└───example_docker-compose.yml  # Example docker-compose setup for the Model API
```

### Logging
The components use the json-formatted logging used by the ELK Stack in square-core/logging.

## Requirements

Python 3.7+, Docker (optional), Make (optional)

## Installation
Install the required packages in your local environment (ideally virtualenv, conda, etc.).
```bash
pip install -r inference_server/requirements1.txt
pip uninstall -y -r inference_server/uninstall_requirements.txt
pip install -r inference_server/requirements2.txt
```
or
```sh
make install
```
**Why two requirement.txt and why the uninstall?**  
`sentence-transformers` depends on `transformers` and it will be installed along with it.
However, we use `adapter-transformers` (a fork of `transformers`) in this project.
Both `transformers` and `adapter-transformers` use the same namespace so they conflict.
Thus, we first install `sentence-transformers` along with `transformers`, 
uninstall `transformers`, and finally install `adapter-transformers`.


## Setup
### Docker
1. Create `auth_server/.env` with secret API key. See [here](auth_server/.env.example) for an example.
2. For each model server that should run, create a `.env.$model` to configure it.  
   See [here](inference_server/.env.example) for an example.
3. Configure `nginx/nginx.conf` to correctly forward requests to each server. The server DNS name has to
   match `container_name` of each server in the `docker-compose.yaml`.
4. Configure `docker-compose.yaml` by adding services for the auth server, nginx (with the config), and the
   model servers (each with their .env file). See [example_docker-compose.yml](example_docker-compose.yml) for an example.
### Local
Create `inference_server/.env` and configure it as needed for your local model server.
You do not need nginx and the authorization server for local testing.

## Running

#### Running Localhost

```sh
make run
```
This *only* starts one inference server using `inference_server/.env`. No nginx, no auth server.  
For debugging, `inference_server/main.py` can also be used as entry.


#### Running Via Docker

```sh
make deploy
```

#### Running Tests
For unit tests:
```sh
make test
```
For load testing with Locust, see [this README](locust/README.md).
