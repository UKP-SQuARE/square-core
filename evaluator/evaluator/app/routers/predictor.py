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
from evaluator.app.models import Prediction, PredictionResult, get_dataset_metadata
from evaluator.app.routers import client_credentials
from evaluator.tasks import predict_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predictor")
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
        f"start predictions with parameters: skill_id={skill_id}; dataset_name={dataset_name}"
    )
    # get dataset metadata
    dataset_metadata = get_dataset_metadata(dataset_name)
    # get the dataset
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.error("Dataset does not exist!")
        raise HTTPException(400, "Dataset does not exist!")
    logger.debug(f"Dataset loaded: {dataset}")
    # format the dataset into universal format for its skill-type
    try:
        dataset = dataset_handler.to_generic_format(dataset, dataset_metadata)
    except ValueError as e:
        logger.error(f"{e}")
        raise HTTPException(400, f"{e}")

    task_id = f"predict-{skill_id}-{dataset_name}"

    task = predict_task.predict.apply_async(
        args=(skill_id, dataset_name, token), task_id=task_id
    )
    return task.id
