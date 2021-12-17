from fastapi import APIRouter
from starlette.requests import Request

from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import PredictionOutputForSequenceClassification, \
    PredictionOutputForTokenClassification, \
    PredictionOutputForQuestionAnswering, PredictionOutputForGeneration, PredictionOutputForEmbedding
from square_model_inference.models.statistics import ModelStatistics
from square_model_inference.core.config import MODEL_TYPE, MODEL_NAME, MODEL_CLASS, DISABLE_GPU, BATCH_SIZE, \
    MAX_INPUT_SIZE

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
    logger.info("Supplieng statistics for ")
    return ModelStatistics(
        model_type=MODEL_TYPE,
        model_name=MODEL_NAME,
        model_class=MODEL_CLASS,
        batch_size=BATCH_SIZE,
        max_input=MAX_INPUT_SIZE,
        disable_gpu=DISABLE_GPU,
    )
