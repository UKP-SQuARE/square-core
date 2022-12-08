import datetime
import logging
from typing import Dict, List

import requests
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
from evaluator.app.core.task_helper import (
    dataset_exists,
    metric_exists,
    skill_exists,
    task_id,
)
from evaluator.app.models import (
    ExtractiveDatasetSample,
    Metric,
    MetricResult,
    MultipleChoiceDatasetSample,
    PredictionResult,
)
from evaluator.app.routers import client_credentials
from evaluator.tasks import evaluate_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluate")
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
    token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"Requested evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' with metric '{metric_name}'"
    )

    # check if the skill exists
    if not skill_exists(skill_id, token):
        msg = f"Skill '{skill_id}' does not exist or you do not have access."
        logger.error(msg)
        raise HTTPException(400, msg)

    # check if the dataset exists
    if not dataset_exists(dataset_name):
        msg = f"Dataset '{dataset_name}' does not exist."
        logger.error(msg)
        raise HTTPException(400, msg)

    # check if the metric exists
    if not metric_exists(metric_name):
        msg = f"Metric '{metric_name}' does not exist."
        logger.error(msg)
        raise HTTPException(400, msg)

    # check if predictions exist
    try:
        prediction_result = PredictionResult.from_mongo(
            mongo_client.client.evaluator.predictions.find_one(
                {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}
            )
        )
        if prediction_result is None:
            raise AttributeError
    except AttributeError:
        msg = f"No predictions found for skill '{skill_id}' on dataset '{dataset_name}'. Make sure to run the prediction first before evaluating."
        logger.error(msg)
        raise HTTPException(404, msg)

    task = evaluate_task.evaluate.apply_async(
        args=(skill_id, dataset_name, metric_name),
        task_id=task_id("evaluate", skill_id, dataset_name, metric_name),
    )
    logger.debug(
        f"Created evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'. Task-ID: '{task.id}'"
    )

    return task.id
