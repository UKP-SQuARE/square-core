import os
import jwt
import logging
import requests

from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import JSONResponse

from app.models.management import GetModelsResult,\
                                  DeployRequest,\
                                  TaskGenericModel,\
                                  TaskResultModel, \
                                  GetModelsHealth, \
                                  UpdateModel
from app.core.config import settings
from app.routers import client_credentials

from tasks.tasks import deploy_task, remove_model_task

from docker_access import get_all_model_prefixes

from square_auth.auth import Auth

from mongo_access import MongoClass


logger = logging.getLogger(__name__)
router = APIRouter()

mongo_client = MongoClass()


async def get_payload_from_token(request: Request):
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)
    return {"realm": realm, "username": payload["preferred_username"]}


def has_auth_header(request: Request):
    return request.headers.get("Authorization", "").lower().startswith("bearer")


@router.get("/deployed-models", name="get-deployed-models", response_model=List[GetModelsResult])
async def get_all_models():  # token: str = Depends(client_credentials)):
    """
    Get all the models deployed on the platform in list format
    """
    models = await mongo_client.get_models_db()
    result = []
    for m in models:
        result.append(GetModelsResult(
            identifier=m["identifier"],
            model_type=m["MODEL_TYPE"],
            model_name=m["MODEL_NAME"],
            disable_gpu=m["DISABLE_GPU"],
            batch_size=m["BATCH_SIZE"],
            max_input=m["MAX_INPUT_SIZE"],
            model_class=m["MODEL_CLASS"],
            return_plaintext_arrays=m["RETURN_PLAINTEXT_ARRAYS"],
        ))
    return result


@router.get("/deployed-models-health", response_model=List[GetModelsHealth], name="get-deployed-models-health")
async def get_all_models(token: str = Depends(client_credentials)):
    models = await mongo_client.get_models_db()
    lst_models = []
    for m in models:
        r = requests.get(
            url="{}/api/{}/health/heartbeat".format(settings.API_URL, m["identifier"]),
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code == 200:
            lst_models.append({"identifier": m["identifier"], "is_alive": r.json()["is_alive"]})
        else:
            lst_models.append({"identifier": m["identifier"], "is_alive": False})

    return lst_models


@router.post("/deploy", name="deploy-model", response_model=TaskGenericModel)
async def deploy_new_model(request: Request, model_params: DeployRequest):
    """
    deploy a new model to the platform
    """
    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]
    else:
        user_id = ""
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
        # "WEB_CONCURRENCY": 2,  # fixed processes, do not give the control to  end-user
    }

    identifier_new = await(mongo_client.check_identifier_new(identifier))
    if not identifier_new:
        raise HTTPException(status_code=401, detail="A model with that identifier already exists")
    res = deploy_task.delay(user_id, identifier, env)
    logger.info(res.id)
    return {"message": f"Queued deploying {identifier}", "task_id": res.id}


@router.delete("/remove/{identifier}", name="remove-model", response_model=TaskGenericModel)
async def remove_model(request: Request, identifier):
    """
    Remove a model from the platform
    """
    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]
    else:
        user_id = ""

    # check if the user deployed a model that he/she is removing
    models = await mongo_client.get_models_db()
    model_config = [m for m in models if m["identifier"] == identifier][0]
    check_user = True if model_config["user_id"] == user_id else False
    if check_user:
        res = remove_model_task.delay(identifier)
    else:
        raise HTTPException(status_code=401, detail="Cannot remove a model deployed by another user")
    return {"message": "Queued removing model.", "task_id": res.id}


@router.put("/update/{identifier}")
async def update_model(identifier: str, update_parameters: UpdateModel, token: str = Depends(client_credentials)):
    await(mongo_client.update_model_db(identifier, update_parameters))
    logger.info("Update parameters Type {},dict  {}".format(type(update_parameters.dict()), update_parameters.dict()))
    r = requests.post(
        url="{}/api/{}/update".format(settings.API_URL, identifier),
        json=update_parameters.dict(),
        headers={"Authorization": f"Bearer {token}"},
        verify=os.getenv("VERIFY_SSL", 1) == 1,
    )
    return {"status_code": r.status_code, "content": r.json()}


@router.get("/task/{task_id}", name="task-status", response_model=TaskResultModel)
async def get_task_status(task_id):
    """
    Get results from a celery task
    """
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': str(task_id), 'status': 'Finished', 'result': result}


@router.put("/db/update")
async def init_db_from_docker(token: str = Depends(client_credentials)):
    lst_prefix, port = get_all_model_prefixes()
    lst_models = []

    for prefix in lst_prefix:
        r = requests.get(
            url="{}{}/stats".format(settings.API_URL, prefix),
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code == 200:
            data = r.json()
            logger.info("Response Format {}".format(data))
            lst_models.append({
                "user_id": "admin",
                "identifier": prefix.split("/")[-1],
                "MODEL_NAME": data["model_name"],
                "MODEL_TYPE": data["model_type"],
                "DISABLE_GPU": data["disable_gpu"],
                "BATCH_SIZE": data["batch_size"],
                "MAX_INPUT_SIZE": data["max_input"],
                "MODEL_CLASS": data["model_class"],
                "RETURN_PLAINTEXT_ARRAYS": data["return_plaintext_arrays"],
                "TRANSFORMERS_CACHE": data["transformers_cache"],
                "MODEL_PATH": data["model_path"],
                "DECODER_PATH": data["decoder_path"],
            })
        else:
            logger.info("Error retrieving Model Statistics: {}".format(r.json()))
    added_models = await(mongo_client.init_db(lst_models))
    return {"added": added_models}


@router.post("/db/deploy")
async def start_from_db(token: str = Depends(client_credentials)):
    configs = await mongo_client.get_models_db()
    deployed = []
    tasks = []
    for model in configs:
        r = requests.get(
            url="{}/api/{}/health/heartbeat".format(settings.API_URL, model["identifier"]),
            headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code != 200:
            identifier = model["identifier"]
            env = model
            del env["identifier"]
            del env["_id"]
            res = deploy_task.delay(identifier, env)
            logger.info(res.id)
            deployed.append(identifier)
            tasks.append(res.id)

    return {"message": f"Queued deploying {deployed}", "task_id": tasks}
