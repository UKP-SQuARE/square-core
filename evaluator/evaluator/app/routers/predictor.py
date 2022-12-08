import datetime
import json
import logging
from typing import Dict, List

import requests
from bson import ObjectId
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.core import DatasetHandler
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError
from evaluator.app.core.task_helper import dataset_exists, skill_exists, task_id
from evaluator.app.models import Prediction, PredictionResult
from evaluator.app.routers import client_credentials
from evaluator.tasks import predict_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict")
auth = Auth()


@router.post(
    "/{skill_id}/{dataset_name}",
    status_code=202,
)
async def predict(
    request: Request,
    skill_id: str,
    dataset_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"Requested prediction-task for skill '{skill_id}' on dataset '{dataset_name}'"
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

    task = predict_task.predict.apply_async(
        args=(skill_id, dataset_name, token),
        task_id=task_id("predict", skill_id, dataset_name),
    )
    logger.debug(
        f"Created prediction-task for skill '{skill_id}' on dataset '{dataset_name}'. Task-ID: '{task.id}'"
    )

    return task.id
