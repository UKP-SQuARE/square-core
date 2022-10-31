import logging
import os

from app.models.prediction import AsyncTaskResult
from app.models.request import PredictionRequest, Task
from app.models.statistics import ModelStatistics, UpdateModel
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse
from tasks.config.model_config import ModelConfig
from tasks.tasks import prediction_task

logger = logging.getLogger(__name__)

router = APIRouter()
QUEUE = os.getenv("QUEUE", os.getenv("MODEL_NAME", None))


def check_valid_request(request):
    if request.input is None:
        return False, "Missing input"
    return True, None


@router.post(
    "/{identifier}/sequence-classification",
    response_model=AsyncTaskResult,
    name="sequence classification",
)
@router.post(
    "/{hf_username}/{identifier}/sequence-classification",
    response_model=AsyncTaskResult,
    name="sequence classification",
)
async def sequence_classification(
    identifier: str, prediction_request: PredictionRequest, hf_username: str = None
) -> AsyncTaskResult:
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    valid, msg = check_valid_request(prediction_request)
    if not valid:
        return HTTPException(status_code=422, detail=msg)
    model_config = ModelConfig.load_from_file(identifier)
    res = prediction_task.apply_async(
        (
            prediction_request.dict(),
            Task.sequence_classification,
            model_config.to_dict(),
        ),
        queue=identifier.replace("/", "-"),
    )

    return AsyncTaskResult(message="Queued sequence classification", task_id=res.id)


@router.post(
    "/{identifier}/token-classification",
    response_model=AsyncTaskResult,
    name="token classification",
)
@router.post(
    "/{hf_username}/{identifier}/token-classification",
    response_model=AsyncTaskResult,
    name="token classification",
)
async def token_classification(
    identifier: str, prediction_request: PredictionRequest, hf_username: str = None
) -> AsyncTaskResult:
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    valid, msg = check_valid_request(prediction_request)
    if not valid:
        return HTTPException(status_code=422, detail=msg)
    model_config = ModelConfig.load_from_file(identifier)
    res = prediction_task.apply_async(
        (prediction_request.dict(), Task.token_classification, model_config.to_dict()),
        queue=identifier.replace("/", "-"),
    )
    return AsyncTaskResult(message="Queued token classification", task_id=res.id)


@router.post(
    "/{identifier}/embedding", response_model=AsyncTaskResult, name="embedding"
)
@router.post(
    "/{hf_username}/{identifier}/embedding",
    response_model=AsyncTaskResult,
    name="embedding",
)
async def embedding(
    identifier: str, prediction_request: PredictionRequest, hf_username: str = None
) -> AsyncTaskResult:
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    valid, msg = check_valid_request(prediction_request)
    if not valid:
        return HTTPException(status_code=422, detail=msg)
    model_config = ModelConfig.load_from_file(identifier)
    res = prediction_task.apply_async(
        (prediction_request.dict(), Task.embedding, model_config.to_dict()),
        queue=identifier.replace("/", "-"),
    )
    return AsyncTaskResult(message="Queued embedding", task_id=res.id)


@router.post(
    "/{identifier}/question-answering",
    response_model=AsyncTaskResult,
    name="question answering",
)
@router.post(
    "/{hf_username}/{identifier}/question-answering",
    response_model=AsyncTaskResult,
    name="question answering",
)
async def question_answering(
    identifier: str, prediction_request: PredictionRequest, hf_username: str = None
) -> AsyncTaskResult:
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    valid, msg = check_valid_request(prediction_request)
    if not valid:
        return HTTPException(status_code=422, detail=msg)
    model_config = ModelConfig.load_from_file(identifier)
    res = prediction_task.apply_async(
        (prediction_request.dict(), Task.question_answering, model_config.to_dict()),
        queue=identifier.replace("/", "-"),
    )
    return AsyncTaskResult(message="Queued question answering", task_id=res.id)


@router.post(
    "/{identifier}/generation", response_model=AsyncTaskResult, name="generation"
)
@router.post(
    "/{hf_username}/{identifier}/generation",
    response_model=AsyncTaskResult,
    name="generation",
)
async def generation(
    identifier: str, prediction_request: PredictionRequest, hf_username: str = None
) -> AsyncTaskResult:
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    valid, msg = check_valid_request(prediction_request)
    if not valid:
        return HTTPException(status_code=422, detail=msg)
    model_config = ModelConfig.load_from_file(identifier)
    res = prediction_task.apply_async(
        (prediction_request.dict(), Task.generation, model_config.to_dict()),
        queue=identifier.replace("/", "-"),
    )
    return AsyncTaskResult(message="Queued token classification", task_id=res.id)


@router.get("/task_result/{task_id}")
async def get_task_results(task_id: str):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(
            status_code=202, content={"task_id": str(task_id), "status": "Processing"}
        )
    result = task.get()
    return {"task_id": str(task_id), "status": "Finished", "result": result}


@router.get("/{identifier}/stats", response_model=ModelStatistics, name="statistics")
@router.get(
    "/{hf_username}/{identifier}/stats",
    response_model=ModelStatistics,
    name="statistics",
)
async def statistics(identifier: str, hf_username: str = None) -> ModelStatistics:
    """
    Returns the statistics of the model
    :return: the ModelStatistics for the model
    """
    logger.info("Getting statistics for ")
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    return get_statistics(identifier)


@router.post("/{identifier}/update")
@router.post("/{hf_username}/{identifier}/update")
async def update(identifier: str, updated_param: UpdateModel, hf_username: str = None):
    """
    Update the model with the given parameters.
    (not all parameters can be updated through this method e.g. the model class
    is linked to the model, hence it can't be updated during runtime)
    :param updated_param: the new parameters
    :return: the information about the updated model
    """
    logger.info("Updating model parameters with {}".format(updated_param))
    if hf_username:
        identifier = f"{hf_username}/{identifier}"
    model_config = ModelConfig.load_from_file(identifier)
    if (
        model_config.model_type in ["onnx", "sentence-transformer"]
        and model_config.disable_gpu != updated_param.disable_gpu
    ):
        raise HTTPException(
            status_code=400, detail="Can't change gpu setting for the model"
        )
    model_config.disable_gpu = updated_param.disable_gpu
    model_config.batch_size = updated_param.batch_size
    model_config.max_input_size = updated_param.max_input
    model_config.return_plaintext_arrays = updated_param.return_plaintext_arrays
    logger.info(model_config)
    model_config.save(identifier)
    logger.info(model_config)
    return model_config.to_statistics()


def get_statistics(identifier):
    """
    Get the information about the model
    :return: the ModelStatistics for the model
    """
    logger.info("Reloading config")
    model_config = ModelConfig.load_from_file(identifier)
    model_config.update()
    logger.info(model_config)
    return model_config.to_statistics()
