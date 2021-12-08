# SQuARE Model API
Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## On the API Path
The 'true' path of the API for the model server is of the form `/api/$endpoint` where the endpoint
is embeddings, question-answering, etc. This is the path you use if you just run a model server locally.

However, to run and distinguish multiple models, we use an API gateway with traefik so we extend 
the path to `/$model-prefix/api/$endpoint` which is then resolved by traefik to the correct model server and forwarded
to this server's `/api/$endpoint` endpoint. This is the path you use with Docker.
This requires you to setup the docker-compose and treafik config as described below.

## Project structure

The Model API uses 2 components: 
n inference servers (each with their own model), and a treafik server that serves as API gateway 
to forward requests to the correct inference server and to handle authorization of requests.
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
1. For each model server that should run, create a `.env.$model` to configure it.  
   See [here](inference_server/.env.example) for an example.
2. Configure `docker-compose.yaml` by adding services for the treafik reverse proxy, and the
   model servers (each with their .env file). See [example_docker-compose.yml](docker-compose.yml) for an example.
### Local
Create `inference_server/.env` and configure it as needed for your local model server.

## Running

#### Running Localhost

```sh
make run
```
This *only* starts one inference server using `inference_server/.env`. No treafik, no auth server.  
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

#### Adding new Models
With treafik we can add new models to the model API easily for each new model append the following to the 
docker-compse file:

```dockerfile
inference_<model>:
    image: ukpsquare/square-model-api:latest
    env_file:
      - ./inference_server/.env.<model>
    volumes:
      - ./.cache/:/etc/huggingface/.cache/

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.<model>.rule=PathPrefix(`/<model-prefix>`)"
```

And save the model configurations in the `.env.<model>` file. The `model-prefix` is the prefix under which the 
corresponding instance of the model-api is reachable.

#### Adding new Users
The traefic component provides an Authentification service. To add new users and their password add 
them [here](traefic.yaml). All users have the following form: 
```
<user-name>:<password-hash>
```
The password can be hashed using wither MD5, SHA-1 or BCrypt.
It is easiest to use `htpasswd` to obtain the necessary hash.
The default `admin` user has the password `example_key`.
