import os
import logging
import requests

from typing import List

from fastapi import APIRouter, HTTPException

from app.models.management import GetModelsResult, DeployRequest, DeployResult, RemoveResult
from app.core.config import settings

from docker_access import start_new_model_container, get_all_model_prefixes, remove_model_container

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/deployed-models", response_model=List[GetModelsResult], name="get-deployed-models")
async def get_all_models():  # token: str = Depends(client_credentials)):
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


@router.post("/deploy", response_model=DeployResult, name="deploy-model")
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
    logger.debug(env)
    try:
        container = start_new_model_container(identifier, env)
        logger.debug(container)
        response_body = {
                "success": True,
                "container": container.id,
                "message": "Model deployment in progress. Check the `/api/models/deployed-models` "
                           "endpoint for more info."
            }

        if container:
            deployment_result = response_body
            return deployment_result
    except:
        logger.exception("Deployment failed", exc_info=True)

    raise HTTPException(status_code=400, detail="Deployment unsuccessful")


@router.post("/remove/{identifier}", response_model=RemoveResult, name="remove-model")
async def remove_model(identifier):
    """
    Remove a model from the platform
    """
    try:
        result = remove_model_container(identifier)
        if result:
            return {
                "success": result,
                "message": "Model removal successful"
            }
    except:
        logger.exception("Could not remove model", exc_info=True)
    raise HTTPException(status_code=400, detail="Model removal unsuccessful")
