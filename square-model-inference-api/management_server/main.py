import os
from fastapi import FastAPI, HTTPException, UploadFile, File

import requests
from models import ModelRequest
from docker_access import start_new_model_container, get_all_model_prefixes, remove_model_container, get_port

API_URL = "http://172.17.0.1"
ONNX_DEFAULT = "../square-model-inference-api/inference-server/onnx_models"

app = FastAPI()


@app.get("/api")
async def get_all_models():
    lst_prefix = get_all_model_prefixes()
    port = get_port()
    lst_models = []
    for prefix in lst_prefix:
        r = requests.get(url="{}:{}{}/stats".format(API_URL, port, prefix), auth=('admin', 'example_key'))
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code == 200:
            lst_models.append(r.json())

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
        "PRELOADED_ADAPTERS": model_params.preloaded_adapters,
    }
    container = start_new_model_container(identifier, env)

    if container:
        return {
            "success": True,
            "container": container.id,
        }
    return HTTPException(status_code=400)


@app.post("/api/remove/{identifier}")
async def remove_model(identifier):
    return {"success": remove_model_container(identifier)}