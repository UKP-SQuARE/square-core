# SQuARE Model API

Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## Project structure

The Model API uses 2 components: 
n inference servers (each with their own model), and a Traefik server that serves as API gateway 
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
├───management_server           # FastAPI server for adding new models or listing all models
│   ├───main.py                 # Entry point in server
│   ├───docker_access.py        # Manages docker acces of server
│   ├───Dockerfile              # Dockerfile for server
│   └───app
│        ├───core               # app config
│        ├───models             # input and output request models
│        └───routers            # api routes
├───traefik
│   └───traefik.yaml            # the midleware of the traefik server (including the Authetification)
├───locust                      # Load testing configuration with Locust
└───docker-compose.yml          # Example docker-compose setup for the Model API
```

## API Path
The 'true' path of the API for the model server is of the form `/api/$endpoint` where the endpoint
is embeddings, question-answering, etc. This is the path you use if you just run a model server locally.

However, to run and distinguish multiple models, we use an API gateway with Traefik so we extend 
the path to `/api/$model-prefix/$endpoint` which is then resolved by Traefik to the correct model server and forwarded
to this server's `/api/$endpoint` endpoint. This is the path you use with Docker.
This requires you to setup the docker-compose and Traefik config as described below.


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
2. Configure `docker-compose.yaml` by adding services for the Traefik reverse proxy, and the
   model servers (each with their .env file). See [docker-compose.yml](docker-compose.yml) for an example.

To test whether the api is running you can execute:

```bash
curl https://square.ukp-lab.de/api/facebook-dpr-question_encoder-single-nq-base/health/heartbeat
```
or if you are running SQuARE in your local machine:
```bash
curl --insecure https://localhost:8443/api/facebook-dpr-question_encoder-single-nq-base/health/heartbeat
```

### Local
Create `inference_server/.env` and configure it as needed for your local model server.

## Running

#### Running Localhost

```sh
make run
```
This *only* starts one inference server using `inference_server/.env`. No Traefik.  
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
  "return_plaintext_arrays": false
}
```

The server will automatically create the model-api instance and add it to the docker network. It might take some time 
until the model is available, since it needs to download and initialize the necessary models and adapters first. 
To check whether the model is ready, you can retrieve all available models and check whether the added models are in the list with the following command:

```bash
curl https://square.ukp-lab.de/api/models/deployed-models

```
or if you are running SQuARE in your local machine:
```bash
curl --insecure https://localhost:8443/api/models/deployed-models`
```

#### Example deployment request 

Deploy distilbert from sentence-transformers.

```bash
curl --request POST 'https://square.ukp-lab.de/api/models/deploy' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
  "identifier": "distilbert",
  "model_name": "msmarco-distilbert-base-tas-b",
  "model_type": "sentence-transformer",
  "disable_gpu": true,
  "batch_size": 32,
  "max_input": 1024,
  "transformer_cache": "\/etc\/huggingface\/.cache\/",
  "model_class": "base",
  "return_plaintext_arrays": false
}'
```

Here, `identifier` is the name you want to give to the model in SQuARE. `model_name` is the name of the model in Transformer's ModelHub, and `model_type` can take the values `sentence-transformer`, `adapter`, `transformer`, and `onnx`.

Another example for BART 
```bash
curl --request POST 'https://square.ukp-lab.de/api/models/deploy' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
  "identifier": "bart-base",
  "model_name": "facebook/bart-base",
  "model_type": "transformer",
  "disable_gpu": true,
  "batch_size": 32,
  "max_input": 1024,
  "transformer_cache": "\/etc\/huggingface\/.cache\/",
  "model_class": "base",
  "return_plaintext_arrays": false
}'
```

#### Example prediction request 

Get prediction from the deployed model.

```bash
curl --request POST 'https://square.ukp-lab.de/api/msmarco-distilbert-base-tas-b/embedding' \
--header 'Content-Type: application/json' \
--data-raw '{
  "input": [
    "Do aliens exist?"
  ],
  "is_preprocessed": false,
  "preprocessing_kwargs": {},
  "model_kwargs": {},
  "task_kwargs": {},
  "adapter_name": ""
}'
```


### Adding new Models Manually
With Traefik we can add new models to the model API easily for each new model append the following to the 
docker-compose file:

```dockerfile
services:
    inference_<model>:
        image: ukpsquare/square-model-api-v1:latest
        env_file:
          - ./inference_server/.env.<model>
        volumes:
          - ./.cache/:/etc/huggingface/.cache/
        labels:
          - "traefik.enable=true"
          - "traefik.http.routers.<model>.rule=PathPrefix(`/api/<model-prefix>`)"
          - "traefik.http.routers.<model>.entrypoints=websecure"
          - "traefik.http.routers.<model>.tls=true"
          - "traefik.http.routers.<model>.tls.certresolver=le"
          - "traefik.http.routers.<model>.middlewares=<model>-stripprefix,<model>-addprefix"
          - "traefik.http.middlewares.<model>-stripprefix.stripprefix.prefixes=/api/<model-prefix>"
          - "traefik.http.middlewares.<model>-addprefix.addPrefix.prefix=/api"
```

And save the model configurations in the `.env.<model>` file. The `model-prefix` is the prefix under which the 
corresponding instance of the model-api is reachable.

#### Adding Onnx models 
Onnx models require a path to the file containing the onnx models. On the VM there are the following files already uploaded:
```
└───onnx_models           
    ├───facebook-bart-base
    │   ├───decoder.onnx
    │   └───model.onnx
    ├───bert-base-uncased          
    │   └───model.onnx
    ├───roberta-base    
    │   └───model.onnx            
    └───t5
        ├───decoder.onnx
        └───model.onnx             
```

This is already configured as a volume in the `docker-compose` file. You have to add the following to your model container:
```
    volumes:
      - onnx-models:/onnx_models
```

Then the model path in the `.env` file has the `onnx_models`folder as root. For example, loading
the BERT model requires the following path `MODEL_PATH=/onnx_models/bert-base-cased/model.onnx`.

In order to be able to start onnx models manually, make sure that the `ONNX_VOLUME` environment variable contains the name of the docker 
volume with the onnx files. Then, simply specify the `model_path` and optionally the `decoder_path` to load a new onnx model. 

### Removing models via API
Removing the deployed distilbert model.
```bash
curl --request POST 'https://square.ukp-lab.de/api/models/remove/distilbert'
```

### Update model parameters

You can update the batch size, gpu option, input size and the type of returned arrays
via our update API. An example request to change the `return_plaintext_arrays` 
param to `true` for the dpr model is shown below:

```bash
curl --request POST 'https://square.ukp-lab.de/api/facebook-dpr-question_encoder-single-nq-base/update' \
--header 'Content-Type: application/json' \
--data-raw '{
  "disable_gpu": true,
  "batch_size": 32,
  "max_input": 1024,
  "return_plaintext_arrays": true
}'
```

Note that changing the `disable_gpu` parameter is only possible for transformer and adapter models. For Onnx models
and sentence-transformers models, changing this parameter is not supported.

### Adding new Users
The Traefik component provides an Authentication service. To add new users and their password add 
them [here](traefik/traefik.yaml). All users have the following form: 
```
<user-name>:<password-hash>
```
The password can be hashed using wither MD5, SHA-1 or BCrypt.
It is easiest to use `htpasswd` to obtain the necessary hash.

The default `admin` user has the password `example_key`.
