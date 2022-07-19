from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import PredictionOutputForSequenceClassification, \
    PredictionOutputForTokenClassification, \
    PredictionOutputForQuestionAnswering, PredictionOutputForGeneration, PredictionOutputForEmbedding
from square_model_inference.models.statistics import ModelStatistics, UpdateModel
from square_model_inference.core.config import model_config

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sequence-classification", response_model=PredictionOutputForSequenceClassification,
             name="sequence classification")
async def sequence_classification(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionOutputForSequenceClassification:
    logger.info(f"Sequence Classification Request: {prediction_request.dict()}")
    model = request.app.state.model  # Access model from global app state
    prediction = await model.predict(prediction_request, Task.sequence_classification)

    return prediction


@router.post("/token-classification", response_model=PredictionOutputForTokenClassification,
             name="token classification")
async def token_classification(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionOutputForTokenClassification:
    logger.info(f"Token Classification Request: {prediction_request.dict()}")
    model = request.app.state.model
    prediction = await model.predict(prediction_request, Task.token_classification)

    return prediction


@router.post("/embedding", response_model=PredictionOutputForEmbedding, name="embedding")
async def embedding(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionOutputForEmbedding:
    logger.info(f"Embedding Request: {prediction_request.dict()}")
    model = request.app.state.model
    prediction = await model.predict(prediction_request, Task.embedding)

    return prediction


@router.post("/question-answering", response_model=PredictionOutputForQuestionAnswering, name="question answering")
async def question_answering(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionOutputForQuestionAnswering:
    logger.info(f"Question Answering Request: {prediction_request.dict()}")
    model = request.app.state.model
    prediction = await model.predict(prediction_request, Task.question_answering)

    return prediction


@router.post("/generation", response_model=PredictionOutputForGeneration, name="generation")
async def generation(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionOutputForGeneration:
    logger.info(f"Generation Request: {prediction_request.dict()}")
    model = request.app.state.model
    prediction = await model.predict(prediction_request, Task.generation)

    return prediction


@router.get("/stats", response_model=ModelStatistics, name="statistics")
async def statistics() -> ModelStatistics:
    """
    Returns the statistics of the model
    :return: the ModelStatistics for the model
    """
    logger.info("Getting statistics for ")
    return get_statistics()


@router.post("/update")
async def update(updated_param: UpdateModel):
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
    return get_statistics()


def get_statistics():
    """
    Get the information about the model
    :return: the ModelStatistics for the model
    """
    return model_config.to_statistics()
