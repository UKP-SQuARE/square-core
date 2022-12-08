import datetime
import json
import logging
from typing import Dict, List

import requests
from bson import ObjectId
from celery.utils.log import get_task_logger
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.core import DatasetHandler
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError
from evaluator.app.core.task_helper import task_id
from evaluator.app.models import Prediction, PredictionResult, get_dataset_metadata
from evaluator.app.routers import client_credentials
from evaluator.tasks import evaluate_task

from .celery import app as celery_app

logger = get_task_logger(__name__)


@celery_app.task
def predict(
    skill_id: str,
    dataset_name: str,
    # dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token: str = Depends(client_credentials),
):
    logger.info(
        f"start predictions with parameters: skill_id={skill_id}; dataset_name={dataset_name}"
    )
    # get dataset metadata
    dataset_metadata = get_dataset_metadata(dataset_name)

    dataset_handler = DatasetHandler()

    # get the dataset
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.error("Dataset does not exist!")
        raise DatasetDoesNotExistError(dataset_name)
    logger.info(f"Dataset loaded: {dataset}")

    # format the dataset into universal format for its skill-type
    try:
        dataset = dataset_handler.to_generic_format(dataset, dataset_metadata)
    except ValueError as e:
        logger.error(f"{e}")

        raise ValueError(f"{e}")

    headers = {"Authorization": f"Bearer {token}"}

    predictions: List[Prediction] = []
    start_time = datetime.datetime.now()

    for i in range(8):
        reference_data = dataset[i]

        if dataset_metadata["skill-type"] == "extractive-qa":
            # 62c1ae1b536b1bb18ff91ce3 # squad
            query_request = {
                "query": reference_data["question"],
                "skill_args": {"context": reference_data["context"]},
                "num_results": 1,
            }
        elif dataset_metadata["skill-type"] == "multiple-choice":
            # 62c1ae19536b1bb18ff91cde # commonsense_qa
            query_request = {
                "query": reference_data["question"],
                "skill_args": {"choices": reference_data["choices"]},
                "num_results": 1,
            }
        else:
            skill_type = dataset_metadata["skill-type"]
            raise ValueError(
                f"Predictions on '{skill_type}' datasets is currently not supported."
            )

        response = requests.post(
            f"https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}/query",
            headers=headers,
            data=json.dumps(query_request),
        )
        prediction_response = response.json()["predictions"][0]

        predictions.append(
            Prediction(
                id=reference_data["id"],
                output=prediction_response["prediction_output"]["output"],
                output_score=prediction_response["prediction_output"]["output_score"],
            )
        )

    calculation_time = (datetime.datetime.now() - start_time).total_seconds()
    logger.info(f"Prediction finished in {calculation_time} seconds: {predictions}")

    prediction_result = PredictionResult(
        skill_id=ObjectId(skill_id),
        dataset_name=dataset_name,
        last_updated_at=datetime.datetime.now(),
        calculation_time=calculation_time,
        predictions=predictions,
    )

    if hasattr(mongo_client, "client") == False:
        logger.info("Lets connect to the mongo client...")
        mongo_client.connect()
    logger.info(f"mongo_client.client = {mongo_client.client}")

    mongo_client.client.evaluator.predictions.replace_one(
        {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name},
        prediction_result.dict(),
        upsert=True,
    )

    logger.info(f"Data saved in database")

    # Trigger evaluation task with default metric
    try:
        logger.info("Trigger evaluation task ...")

        task = evaluate_task.evaluate.apply_async(
            args=(skill_id, dataset_name, dataset_metadata["metric"]),
            task_id=task_id(
                "evaluate", skill_id, dataset_name, dataset_metadata["metric"]
            ),
        )

        logger.info(f"Task with id '{task.id}'")

    except AttributeError:
        logger.info(
            f"Attribute error: Dataset metadata does not have 'metric': {dataset_metadata}"
        )
