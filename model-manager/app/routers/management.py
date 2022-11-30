"""
This file contains all the API calls for the
management server of the models component of SQuARE.
"""

import logging
import os
import uuid
from typing import List
import docker
import traceback

import requests
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.models.management import (
    DeployRequest,
    GetModelsHealth,
    GetModelsResult,
    GetExplainersResult,
    TaskGenericModel,
    TaskResultModel,
    UpdateModel,
)
from app.routers import client_credentials, utils
from app.db.database import MongoClass
from docker_access import get_all_model_prefixes

from tasks import tasks
from tasks.celery import app as celery_app
import json
from bson import json_util


logger = logging.getLogger(__name__)
router = APIRouter()

mongo_client = MongoClass()


@router.get("/deployed-models", name="get-deployed-models", response_model=List[GetModelsResult])
async def get_all_models():  # token: str = Depends(client_credentials)):
    """
    Get all the models deployed on the platform in list format
    """
    models = await mongo_client.get_models_db()
    result = []
    for model in models:
        result.append(
            GetModelsResult(
                identifier=model["IDENTIFIER"],
                model_type=model["MODEL_TYPE"],
                model_name=model["MODEL_NAME"],
                disable_gpu=model["DISABLE_GPU"],
                batch_size=model["BATCH_SIZE"],
                max_input=model["MAX_INPUT_SIZE"],
                model_class=model["MODEL_CLASS"],
                return_plaintext_arrays=model["RETURN_PLAINTEXT_ARRAYS"],
            )
        )
    return result


@router.get("/explainers", name="get-explanation-methods", response_model=List[GetExplainersResult])
async def list_exp_methods():
    """
    Get all the explanation methods for models
    """
    exp_methods = [
        {
            "identifier": "simple_grads", "name": "Vanilla gradients",
            "description": "The attributions are calculated considering the model "
                           "gradients multiplied by the input text embeddings."
        },
        {
            "identifier": "integrated_grads", "name": "Integrated gradients",
            "description": "The attributions are calculated considering the "
                           "integral of the model gradients with respect to the word "
                           "embedding layer along a straight path from a "
                           "baseline instance  to the input instance  "},
        {
            "identifier": "smooth_grads", "name": "Smooth gradients",
            "description": "Take random samples in neighborhood of an input, "
                           "and average the resulting saliency maps. These "
                           "random samples are inputs with added noise."
        },
        {
            "identifier": "attention", "name": "Attention",
            "description": "Based on the model attention weights from the last layer."
        },
        {
            "identifier": "scaled_attention", "name": "Scaled attention",
            "description": "The attention weights are multiplied with their "
                           "gradients to get the token attributions."
        },
    ]
    result = []
    for e in exp_methods:
        result.append(
            GetExplainersResult(
                identifier=e["identifier"],
                method_name=e["name"],
                description=e["description"]
            )
        )
    return result


@router.get("/deployed-models-health", name="get-deployed-models", response_model=List[GetModelsHealth])
async def get_all_models_health():
    '''
    Check all worker's health (worker : inference model container)
    Return:
        result[list]: the health of deployed workers/models.
    '''

    models = await mongo_client.get_models_db()
    result = []
    docker_client = docker.from_env()

    for model in models:
        container_id = mongo_client.get_container_id(model["IDENTIFIER"])
        container_obj = docker_client.containers.get(container_id)
        if container_obj in docker_client.containers.list():
            result.append(
                GetModelsHealth(
                    identifier=model["IDENTIFIER"],
                    is_alive=True,
                )
            )
        else:
            result.append(
                GetModelsHealth(
                    identifier=model["IDENTIFIER"],
                    is_alive=False,
                )
            )
    return result


@router.get("/deployed-model-workers", name="get-deployed-models",)
async def get_model_containers():  # token: str = Depends(client_credentials)):
    """
    Get all the models deployed on the platform in list format
    """
    models = await mongo_client.get_model_containers()
    result = []
    for m in models:
        result.append(
            {
                "identifier": m["_id"],
                "num_containers": m["count"],
            }
        )
    return result


@router.post("/deploy", name="deploy-model", response_model=TaskGenericModel)
async def deploy_new_model(request: Request, model_params: DeployRequest):
    """
    deploy a new model to the platform
    """
    user_id = await utils.get_user_id(request)
    env = {
        "USER_ID": user_id,
        "IDENTIFIER": model_params.model_name,
        "UUID": str(uuid.uuid1()),
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
        "WEB_CONCURRENCY": os.getenv("WEB_CONCURRENCY", 1),  # fixed processes, do not give the control to  end-user
        "KEYCLOAK_BASE_URL": os.getenv("KEYCLOAK_BASE_URL", "https://square.ukp-lab.de"),
        "VERIFY_ISSUER": os.getenv("VERIFY_ISSUER", "1")
    }

    identifier_new = await (mongo_client.check_identifier_new(env["IDENTIFIER"]))
    if not identifier_new:
        raise HTTPException(status_code=406, detail="A model with that identifier already exists")
    res = tasks.deploy_task.delay(env)
    logger.info(res.id)
    return {"message": f"Queued deploying {env['IDENTIFIER']}", "task_id": res.id}


@router.delete("/remove/{identifier}", name="remove-model", response_model=TaskGenericModel)
@router.delete("/remove/{hf_username}/{identifier}", name="remove-model", response_model=TaskGenericModel)
async def remove_model(request: Request, identifier: str, hf_username: str = None):
    """
    Remove a model from the platform
    """
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    # check if the model is deployed
    logger.info(identifier)
    check_model_id = await (mongo_client.check_identifier_new(identifier))
    if check_model_id:
        logger.info("The model is already saved in the database.")
        raise HTTPException(status_code=406, detail="A model with the input identifier does not exist")
    # check if the user deployed this model
    if await mongo_client.check_user_id(request, identifier):
        res = tasks.remove_model_task.delay(identifier)
    else:
        raise HTTPException(status_code=403, detail="Cannot remove a model deployed by another user.")
    return {"message": "Queued removing model.", "task_id": res.id}


@router.post("/{identifier}/add_worker/{num}")
async def add_model_container(request: Request, identifier: str, num: int):
    check_model_id = await (mongo_client.check_identifier_new(identifier))
    if check_model_id:
        raise HTTPException(status_code=406, detail="A model with the input identifier does not exist")
    # check if the user deployed this model
    if await mongo_client.check_user_id(request, identifier):
        env = await mongo_client.get_model_stats(identifier)
        env = json.loads(json_util.dumps(env))
        models = await mongo_client.get_model_containers()
        for m in models:
            if m["_id"] == identifier:
                res = tasks.add_worker.delay(identifier, env, m["count"]+1, num)
                return {"message": f"Queued adding worker for {identifier}", "task_id": res.id}
        return {"message": f"No model with that identifier"}
    else:
        raise HTTPException(status_code=403, detail="Cannot remove a model deployed by another user.")


@router.delete("/{identifier}/remove_worker/{num}")
async def remove_model_container(request: Request, identifier: str, num: int):
    check_model_id = await (mongo_client.check_identifier_new(identifier))
    if check_model_id:
        raise HTTPException(status_code=406, detail="A model with the input identifier does not exist")
    if await mongo_client.check_user_id(request, identifier):
        models = await mongo_client.get_model_containers()
        for m in models:
            if m["_id"] == identifier:
                if m["count"] <= num:
                    return HTTPException(status_code=403, detail=f"Only {m['count']} worker left. To remove that remove the whole model.")
        containers = await mongo_client.get_containers(identifier, num)
        res = tasks.remove_worker.delay(containers)
        return {"message": f"Queued removing worker for {identifier}", "task_id": res.id}
    else:
        raise HTTPException(status_code=403, detail="Cannot remove a model deployed by another user.")


@router.patch("/update/{identifier}")
@router.patch("/update/{hf_username}/{identifier}")
async def update_model(
        request: Request,
        identifier: str,
        update_parameters: UpdateModel,
        hf_username: str = None,
        token: str = Depends(client_credentials),
):
    """
    update the model parameters
    """
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    logger.info("Updating model: {}".format(identifier))
    check_model_id = await (mongo_client.check_identifier_new(identifier))
    if check_model_id:
        raise HTTPException(status_code=406, detail="A model with the input identifier does not exist")
    if await mongo_client.check_user_id(request, identifier):
        await (mongo_client.update_model_db(identifier, update_parameters))
        logger.info(
            "Update parameters Type %s,dict  %s", type(update_parameters.dict()), update_parameters.dict()
        )
        response = requests.post(
            url=f"{settings.API_URL}/api/{identifier}/update",
            json=update_parameters.dict(),
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        logger.info("response: {}".format(response.text))

        return {"status_code": response.status_code, "content": response.json()}

    raise HTTPException(status_code=403, detail="Cannot update a model deployed by another user")


@router.get("/task_result/{task_id}", name="task-status", response_model=TaskResultModel)
async def get_task_status(task_id):
    """
    Get results from a celery task
    """
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={"task_id": str(task_id), "status": "Processing"})
    result = task.get()
    return {"task_id": str(task_id), "status": "Finished", "result": result}

@router.get("/task", name="")
async def get_all_tasks():
    # https://docs.celeryq.dev/en/latest/userguide/workers.html#inspecting-workers
    i = celery_app.control.inspect()
    # Show the items that have an ETA or are scheduled for later processing
    scheduled = i.scheduled()

    # Show tasks that are currently active.
    active = i.active()

    # Show tasks that have been claimed by workers
    reserved = i.reserved()

    tasks = {
        "scheduled": scheduled,
        "active": active,
        "reserved": reserved,
    }

    logger.info("/tasks: {}".format(tasks))

    return tasks


@router.put("/db/update")
async def init_db_from_docker(token: str = Depends(client_credentials)):
    """
    update the database with the configuration of models
    deployed but not added to the db
    """
    lst_prefix, lst_container_ids, _ = get_all_model_prefixes()
    lst_models = []

    for prefix, container in zip(lst_prefix, lst_container_ids):
        response = requests.get(
            url="{}/api/main/{}/stats".format(settings.API_URL, prefix),
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if response.status_code == 200:
            data = response.json()
            logger.info("Response Format %s", data)
            lst_models.append(
                {
                    "USER_ID": "ukp",
                    "IDENTIFIER": prefix.split("/")[-1],
                    "MODEL_NAME": data["model_name"],
                    "MODEL_TYPE": data["model_type"],
                    "DISABLE_GPU": data["disable_gpu"],
                    "BATCH_SIZE": data["batch_size"],
                    "MAX_INPUT_SIZE": data["max_input"],
                    "MODEL_CLASS": data["model_class"],
                    "RETURN_PLAINTEXT_ARRAYS": data["return_plaintext_arrays"],
                    "TRANSFORMERS_CACHE": data.get("transformers_cache", ""),
                    "MODEL_PATH": data.get("model_path", ""),
                    "DECODER_PATH": data.get("decoder_path", ""),
                    "CONTAINER": container,
                }
            )
        else:
            logger.info("Error retrieving Model Statistics: %s", response.json())
    added_models = await (mongo_client.init_db(lst_models))
    return {"added": added_models}


@router.post("/db/deploy")
@router.post("/db/deploy/{hf_username}/{identifier}")
async def start_from_db(identifier: str=None, hf_username: str=None, token: str = Depends(client_credentials)):
    """
    deploy models from the database
    """
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    configs = await mongo_client.get_models_db()
    if identifier:
        configs = [config for config in configs if config["IDENTIFIER"] == identifier]

    deployed: list = []
    task_ids: list = []

    for model in configs:
        response = requests.get(
            url=f'{settings.API_URL}/api/main/{model["IDENTIFIER"]}/health/heartbeat',
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if response.status_code != 200:
            identifier = model["IDENTIFIER"]
            env = model
            del env["_id"]
            del env["CONTAINER"]
            res = tasks.deploy_task.delay(env, allow_overwrite=True)
            logger.info(res.id)
            deployed.append(identifier)
            task_ids.append(res.id)

    return {"message": f"Queued deploying {deployed}", "task_id": task_ids}
