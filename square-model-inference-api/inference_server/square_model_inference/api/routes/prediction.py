from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
import os

from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import AsyncTaskResult
from square_model_inference.models.statistics import ModelStatistics, UpdateModel
from starlette.responses import JSONResponse

from tasks.config.model_config import model_config
from tasks.tasks import add_two, prediction_task

import logging

logger = logging.getLogger(__name__)

router = APIRouter()
QUEUE = os.getenv("QUEUE", os.getenv("MODEL_NAME", None))


@router.get("/test")
async def add():
    res = add_two.delay(2, 2)
    return {"message": "Queued add", "task_id": res.id}


@router.post("/sequence-classification", response_model=AsyncTaskResult,
             name="sequence classification")
async def sequence_classification(
        identifier: str,
        prediction_request: PredictionRequest,
) -> AsyncTaskResult:
    res = prediction_task.apply_async((prediction_request.dict(), Task.sequence_classification, model_config.to_dict()), queue=identifier)

    return AsyncTaskResult(message="Queued sequence classification", task_id=res.id)


@router.post("/{identifier}/token-classification", response_model=AsyncTaskResult,
             name="token classification")
async def token_classification(
        identifier: str,
        prediction_request: PredictionRequest,
) -> AsyncTaskResult:
    res = await prediction_task.apply_async((prediction_request.dict(), Task.token_classification, model_config.to_dict()), queue=identifier)
    return AsyncTaskResult(message="Queued token classification", task_id=res.id)


@router.post("/{identifier}/embedding", response_model=AsyncTaskResult, name="embedding")
async def embedding(
        identifier: str,
        prediction_request: PredictionRequest,
) -> AsyncTaskResult:
    res = prediction_task.apply_async((prediction_request.dict(), Task.embedding, model_config.to_dict()), queue=identifier)
    return AsyncTaskResult(message="Queued embedding", task_id=res.id)


@router.post("/{identifier}/question-answering", response_model=AsyncTaskResult, name="question answering")
async def question_answering(
        identifier: str,
        prediction_request: PredictionRequest,
) -> AsyncTaskResult:
    res = prediction_task.apply_async((prediction_request.dict(), Task.question_answering, model_config.to_dict()), queue=identifier)
    return AsyncTaskResult(message="Queued question answering", task_id=res.id)


@router.post("/{identifier}/generation", response_model=AsyncTaskResult, name="generation")
async def generation(
        identifier: str,
        prediction_request: PredictionRequest,
) -> AsyncTaskResult:
    res = prediction_task.apply_async((prediction_request.dict(), Task.generation, model_config), queue=identifier)
    return AsyncTaskResult(message="Queued token classification", task_id=res.id)


@router.get("/task_result/{task_id}")
async def get_task_results(task_id: str):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': str(task_id), 'status': 'Finished', 'result': result}


@router.get("/{identifier}/stats", response_model=ModelStatistics, name="statistics")
async def statistics(identifier) -> ModelStatistics:
    """
    Returns the statistics of the model
    :return: the ModelStatistics for the model
    """
    logger.info("Getting statistics for ")
    return get_statistics(identifier)


@router.post("/{identifier}/update")
async def update(identifier: str, updated_param: UpdateModel):
    """
    Update the model with the given parameters.
    (not all parameters can be updated through this method e.g. the model class
    is linked to the model, hence it can't be updated during runtime)
    :param updated_param: the new parameters
    :return: the information about the updated model
    """
    logger.info("Updating model parameters")
    if model_config.model_type in ["onnx", "sentence-transformer"] and model_config.disable_gpu != updated_param.disable_gpu:
        raise HTTPException(status_code=400, detail="Can't change gpu setting for the model")
    model_config.disable_gpu = updated_param.disable_gpu
    model_config.batch_size = updated_param.batch_size
    model_config.max_input_size = updated_param.max_input
    model_config.return_plaintext_arrays = updated_param.return_plaintext_arrays
    model_config.save(identifier)
    return get_statistics(identifier)


def get_statistics(identifier):
    """
    Get the information about the model
    :return: the ModelStatistics for the model
    """
    logger.info("Reloading config")
    model_config.update(identifier)
    logger.info(model_config)
    return model_config.to_statistics()
