import datetime
import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from square_auth.auth import Auth
from square_skill_api.models import PredictionOutput

from evaluator.app import mongo_client
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.app.core.metric_formatters import Formatter, MetricFormattingError
from evaluator.app.models import (
    ExtractiveDatasetSample,
    Metric,
    MetricResult,
    MultipleChoiceDatasetSample,
    PredictionResult,
    get_dataset_metadata,
)
from evaluator.app.routers import client_credentials
from evaluator.tasks import evaluate_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluator")
auth = Auth()


@router.post(
    "/{skill_id}/{dataset_name}/{metric_name}",
    status_code=201,
)
async def evaluate(
    _request: Request,
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    _token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"start evaluation with parameters: skill_id={skill_id}; dataset_name={dataset_name}; metric_name={metric_name}"
    )

    object_identifier = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}

    # Load the metric from HuggingFace
    try:
        metric = load(metric_name)
    except FileNotFoundError:
        logger.error(f"Metric with name='{metric_name}' not found!")
        raise HTTPException(404, f"Metric with name='{metric_name}' not found!")

    # Load the predictions for the given `skill_id` and `dataset_name` from MongoDB
    try:
        prediction_result = PredictionResult.from_mongo(
            mongo_client.client.evaluator.predictions.find_one(object_identifier)
        )
        if prediction_result is None:
            raise AttributeError
        logger.debug(f"Prediction loaded: {prediction_result}")
    except AttributeError:
        msg = f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!"
        logger.error(msg)
        raise HTTPException(404, msg)
    logger.debug(f"Prediction loaded: {prediction_result}")

    # Load dataset metadata (TODO)
    dataset_metadata = get_dataset_metadata(dataset_name)
    # Load the dataset from DatasetHandler
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.error("Dataset does not exist!")
        raise HTTPException(400, "Dataset does not exist!")

    task_id = f"evaluate-{skill_id}-{dataset_name}-{metric_name}"

    task = evaluate_task.evaluate.apply_async(
        args=(skill_id, dataset_name, metric_name), task_id=task_id
    )
    return task.id
