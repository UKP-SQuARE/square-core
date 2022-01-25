import os
import logging

import requests
from fastapi import FastAPI, HTTPException

from docker_access import get_all_model_prefixes, start_new_model_container
from models import ModelRequest

logger = logging.getLogger(__name__)

# API_URL = "http://172.17.0.1"
# set this ENV varibale to `host.docker.internal` for Mac 
API_URL = os.getenv("DOCKER_HOST_URL", "http://172.17.0.1")
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASSWORD = os.getenv("AUTH_USER", "example_key")

app = FastAPI()


@app.get("/api")
async def get_all_models():
    lst_prefix, port = await(get_all_model_prefixes())
    lst_models = []
    for prefix in lst_prefix:
        r = requests.get(
            url="{}:{}{}/stats".format(API_URL, port, prefix), 
            # auth=(AUTH_USER, AUTH_PASSWORD), 
            verify=os.getenv("VERIFY_SSL", 1) == 1
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code == 200:
            lst_models.append(r.json())
        else:
            logger.debug(f"Model not up yet:\n{r.content}")

    return lst_models


@app.post("/api/deploy")
async def add_new_model(model_params: ModelRequest):
    identifier = model_params.identifier
    env = {
        "MODEL_NAME": model_params.model_name,
        "MODEL_PATH": model_params.model_path,
        "DECODER_PATH": model_params.decoder_path,
        "MODEL_TYPE": model_params.model_type,
        "MODEL_CLASS": model_params.model_class,
        "DISABLE_GPU": model_params.disable_gpu,
        "BATCH_SIZE": model_params.batch_size,
        "MAX_INPUT_SIZE": model_params.max_input,
        "TRANSFORMERS_CACHE": model_params.transformers_cache,
        "RETURN_PLAINTEXT_ARRAYS": model_params.return_plaintext_arrays,

    }
    container = await(start_new_model_container(identifier, env))

    if container:
        return {
            "success": True,
            "container": container.id,
        }
    return HTTPException(status_code=400)
