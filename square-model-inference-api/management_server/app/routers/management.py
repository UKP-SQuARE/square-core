import os
import logging
import requests

from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.models.management import GetModelsResult,\
                                  DeployRequest,\
                                  TaskGenericModel,\
                                  TaskResultModel
from app.core.config import settings
from starlette.responses import JSONResponse
from tasks.tasks import deploy_task, remove_model_task

from docker_access import start_new_model_container,\
                          get_all_model_prefixes, \
                          remove_model_container

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/deployed-models", name="get-deployed-models", response_model=List[GetModelsResult])
async def get_all_models():  # token: str = Depends(client_credentials)):
    """
    Get all the models deployed on the platform in list format
    """
    lst_prefix, port = get_all_model_prefixes()
    lst_models = []

    for prefix in lst_prefix:
        r = requests.get(
            url="{}:{}{}/stats".format(settings.API_URL, port, prefix),
            # headers={"Authorization": f"Bearer {token}"},
            verify=os.getenv("VERIFY_SSL", 1) == 1,
        )
        # if the model-api instance has not finished loading the model it is not available yet
        if r.status_code == 200:
            lst_models.append(r.json())
        else:
            logger.debug(f"Model not up yet:\n{r.content}")

    return lst_models


@router.post("/deploy", name="deploy-model", response_model=TaskGenericModel)
async def deploy_new_model(model_params: DeployRequest):
    """
    deploy a new model to the platform
    """
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
    res = deploy_task.delay(identifier, env)
    logger.info(res.id)
    return {"message": f"Queued deploying {identifier}", "task_id": res.id}


@router.post("/remove/{identifier}", name="remove-model", response_model=TaskGenericModel)
async def remove_model(identifier):
    """
    Remove a model from the platform
    """
    res = remove_model_task.delay(identifier)
    return {"message": "Queued removing model.", "task_id": res.id}


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
