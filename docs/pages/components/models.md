# Models

Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## Project structure

The Model API uses 2 components: 
n inference servers (each with their own model), and a treafik server that serves as API gateway 
to forward requests to the correct inference server and to handle authorization of requests.
```
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
├───management_server          # FastAPI server for adding new models or listing all models
│   ├───main.py                 # Entry point in server
│   ├───docker_access.py        # Manages docker acces of server
│   ├───Dockerfile              # Dockerfile for server
│   └───models.py               # Input modeling of the server
├───traefik
│   └───traefik.yaml            # the midleware of the traefik server (including the Authetification)
├───locust                      # Load testing configuration with Locust
└───example_docker-compose.yml  # Example docker-compose setup for the Model API
```

## Requirements

- Python 3.7+
- Docker (optional)
- Make (optional)

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


## API Path
The 'true' path of the API for the model server is of the form `/api/$endpoint` where the endpoint
is embeddings, question-answering, etc. This is the path you use if you just run a model server locally.

However, to run and distinguish multiple models, we use an API gateway with traefik so we extend 
the path to `/api/$model-prefix/$endpoint` which is then resolved by traefik to the correct model server and forwarded
to this server's `/api/$endpoint` endpoint. This is the path you use with Docker.
This requires you to setup the docker-compose and treafik config as described below.


## Setup
### Docker
1. For each model server that should run, create a `.env.$model` to configure it.  
   See [here](inference_server/.env.example) for an example.
2. Configure `docker-compose.yaml` by adding services for the traefik reverse proxy, and the
   model servers (each with their .env file). See [example_docker-compose.yml](example_docker-compose.yml) for an example.

To test whether the api is running you can execute:
```bash
curl -X GET http://localhost:8989/api/dpr/health/heartbeat  -H 'accept:application/json' --user admin:example_key
```

### Local
Create `inference_server/.env` and configure it as needed for your local model server.

## Running

#### Running Localhost

```sh
make run
```
This *only* starts one inference server using `inference_server/.env`. No treafik.  
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

### Adding new Models using API
New models can be added without manually adapting the docker-compose file by a `POST` request to`api/models/deploy`.
By passing all environment information that would normally be in the `.env` file and the identifier which will be part
 of the path prefix in the following form:
```
{
  "identifier": <model_prefix>,
  "model_name": <model_name>,
  "model_path": <model_path>,
  "decoder_path": <decoder_path>,
  "model_type": <model_type>,
  "disable_gpu": true,
  "batch_size": 32,
  "max_input": 1024,
  "transformer_cache": "../.cache",
  "model_class": <model_class>,
  "return_plaintext_array": false
}
```

The server will automatically create the model-api instance and add it to the docker network. It might take some time 
until the model is available, since it needs to download and initialize the necessary models and adapters first. 
To check whether the model is ready, you can retrieve all available models at `api/models` and check whether the added 
models is in the list.

#### Example deployment request 

Deploy distilbert from sentence-transformers.

```bash
 curl -X POST http://localhost:8989/api/models/deploy  -H 'accept:application/json' -d '{
  "identifier": "distilbert",
  "model_name": "msmarco-distilbert-base-tas-b",
  "model_type": "sentence-transformer",
  "disable_gpu": true,
  "batch_size": 32,
  "max_input": 1024,
  "transformer_cache": "\/etc\/huggingface\/.cache\/",
  "model_class": "base",
  "return_plaintext_array": false
}' --user admin:example_key
```

#### Example prediction request 

Get prediction from the deployed model.

```bash
 curl -X POST http://localhost:8989/api/distilbert/embedding  -H 'accept:application/json' -d '{
  "input": [
    "Do aliens exist?"
  ],
  "is_preprocessed": false,
  "preprocessing_kwargs": {},
  "model_kwargs": {},
  "task_kwargs": {},
  "adapter_name": ""
}' --user admin:example_key
```



### Adding new Models Manually
With treafik we can add new models to the model API easily for each new model append the following to the 
docker-comopse file:

```dockerfile
inference_<model>:
    image: ukpsquare/square-model-api:latest
    env_file:
      - ./inference_server/.env.<model>
    volumes:
      - ./.cache/:/etc/huggingface/.cache/

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.<model>.rule=PathPrefix(`/api/<model-prefix>`)"
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
