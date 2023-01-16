# SQuARE Model API

Inference API that supports SOTA (QA) models & adapters. 
Receives input and returns prediction and other artifacts (e.g. attention scores)

## Project structure

The Model API uses 2 components: 
* A treafik server that redirects incomming requests to the corresponding service
* A main model instance that takes processes all prediction requests and schedules them for the worker with the correct model
* A prediction celery worker that has one specific model loaded and handles the predictions for that model
* A maintaining server that handles adding, removing and updating models and provides some information about the models
* A maintaining celery worker that handles the longer maintaining tasks like deployin a new model
* A mongoDB that contains the currently deployed models and the references to the corresponding docker containers 

This setup allows flexible scaling of the different components.

:warning: This update changes some api answers. For easy access use the ManagementClient 
## API Path
To acces one model for prediction use the path `/api/$model-prefix/$endpoint`, which is then redirected to the main model
server wich schedules the task for the correct worker.

*LOCAL BASE URL* = https://localhost:8443 </br>
*PROD BASE URL* = https://square.ukp-lab.de


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

### Authentication
The authentication service is provided by [Keycloak](https://www.keycloak.org/).

1. Get the bearer token via the following request. The token is valid for 5 minutes.
```python
curl --location --request POST 'https://square.ukp-lab.de/auth/realms/Models-test/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode 'client_id=models' \
--data-urlencode 'client_secret=secret'
```

You can get the client secret from the keycloak console.

2. Pass the received access token to the request. An example to check the model health 
can be seen below:

```python
curl --location --request GET 'https://square.ukp-lab.de/api/facebook-dpr-question_encoder-single-nq-base/health/heartbeat' \
--header 'accept: application/json' \
--header 'Authorization: <access_token>'
```

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

There are also tests that require a running version of the api. To include them run:
```sh
make full-test
```

IMPORTANT: In order to run the client tests add the client secret to the `management_client/pytest.ini` file to the `env`:
```
    CLIENT_SECRET=<client_secret>
```

### Adding new Users
The Traefik component provides an Authentication service. To add new users and their password add 
them [here](traefik/traefik.yaml). All users have the following form: 
```
<user-name>:<password-hash>
```
The password can be hashed using wither MD5, SHA-1 or BCrypt.
It is easiest to use `htpasswd` to obtain the necessary hash.

The default `admin` user has the password `example_key`.

## ManagementClient

It is recommended to use the ManagementClient to access the model-api. It provides methods for all calls to the api, that
already handle the waiting for scheduled tasks.

A prediction with the ManagementClient can be done with the following method:
 
`predict(self, model_identifier, prediction_method, input_data)`
Request model prediction.
`model_identifier` (str): the identifier of the model that should be used for the prediction
`prediction_method` (str): what kind of prediction should be made. Possible values are embedding,
                sequence-classification, token-classification, generation, question-answering
`input_data` (Dict): the input for the prediction

## Management API
The management Api provides methods to manage and maintain the deployed models. You can use this to add, update or
delete models and to get an overview over the deployed models. It also keeps a database that contains all deployed models.
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
  "model_type": "adapter",
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


#### Adding new Models Manually
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

---
**NOTE**

Please don't use the update method from the deployed model. This will not update the database that contains the 
parameters of the deployed model.

---

###Overview over deployed models
To get all deployed models that are currently in the databease call:
`curl --insecure https://localhost:8443/api/models/deployed-models`
This returns all deployed models and their parameters from the database.
If you want to check whether these models are actually running you can access their `is_alive`
status with:
`curl --insecure https://localhost:8443/api/models/deployed-models-health`
This returns the `is_alive`status the individual models returns when `/api/<model-identifier>/health/heartbeat`
is called.

Both of these methods only consider models that are in the database. Models deployed with the management api
are directly added to the database, but manually deployed models are not added by default.

### Scan for models missing from database
To add models to the database (e.g. manually deployed models) call:
`curl --insecure https://localhost:8443/api/models/db/update`
This scans the running docker containers for deployed models and checks whether
they are in the database. If not they are added. The identifiers of all added models are returned.

## Deploy models from database
After a crash or some other failure a model might not be available. To restart all models that have been 
deployed previously send a POST request to `api/models/db/deploy`. It returns all identifiers which it tried to deploy.
For each models a seperate task is queued. Hence, it returns a list of task ids. 

### Queueing
The management server queues background tasks for deploying and removing models. The response to a 
request for deploying or removing a model returns the `task_id`, which can be used to request the 
status of the task. By sending a GET request to:
`/api/models/task/<task_id>`
you can see whether the task has been executed and the results of the task.

### Database
The database is the MongoDB that is also used for the skills and hence uses the credentials specified in the environment
file of that database.


