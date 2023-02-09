import datetime
import json
import logging
import os
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
from evaluator.app.core.dataset_metadata import get_dataset_metadata
from evaluator.app.core.task_helper import task_id
from evaluator.app.models import (
    Evaluation,
    EvaluationStatus,
    Prediction,
    PredictionResult,
)
from evaluator.app.routers import client_credentials
from evaluator.tasks import evaluate_task

from .celery import app as celery_app

logger = get_task_logger(__name__)
base_url = os.getenv("SQUARE_API_URL", "https://square.ukp-lab.de/api")


@celery_app.task
def predict(
    skill_id: str,
    dataset_name: str,
    metric_name: str = None,
    token: str = Depends(client_credentials),
):
    try:
        logger.info(
            f"Started prediction-task for skill '{skill_id}' on dataset '{dataset_name}'"
        )
        if hasattr(mongo_client, "client") == False:
            mongo_client.connect()
        do_predict(skill_id, dataset_name, metric_name, token)
    except Exception as e:
        logger.error(f"{e}")
        evaluation_filter = {
            "skill_id": ObjectId(skill_id),
            "dataset_name": dataset_name,
        }
        mongo_client.client.evaluator.evaluations.update_many(
            evaluation_filter,
            {
                "$set": {
                    "prediction_status": EvaluationStatus.failed,
                    "prediction_error": f"{e}",
                }
            },
        )
        raise e


def do_predict(
    skill_id: str,
    dataset_name: str,
    metric_name: str = None,
    token: str = Depends(client_credentials),
):
    if hasattr(mongo_client, "client") == False:
        mongo_client.connect()

    evaluation_filter = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}
    mongo_client.client.evaluator.evaluations.update_many(
        evaluation_filter, {"$set": {"prediction_status": EvaluationStatus.started}}
    )

    # get dataset metadata
    dataset_metadata = get_dataset_metadata(dataset_name)
    # get the dataset
    dataset_handler = DatasetHandler()
    dataset = dataset_handler.get_dataset(dataset_name)
    # format the dataset into universal format for its skill-type
    dataset = dataset_handler.to_generic_format(dataset, dataset_metadata)

    headers = {"Authorization": f"Bearer {token}"}
    predictions: List[Prediction] = []
    start_time = datetime.datetime.now()

    if dataset_metadata.skill_type == "extractive-qa":
        qa_type = "context"
    elif dataset_metadata.skill_type == "multiple-choice":
        qa_type = "choices"
    else:
        skill_type = dataset_metadata.skill_type
        raise ValueError(
            400,
            f"Predictions on '{skill_type}' datasets is currently not supported.",
        )

    query_request = {
        "query": [
            datapoint["question"] for datapoint in dataset if "question" in datapoint
        ],
        "skill_args": {
            "context": [
                datapoint[qa_type] for datapoint in dataset if qa_type in datapoint
            ]
        },
        "num_results": 1,
    }

    response = requests.post(
        f"{base_url}/skill-manager/skill/{skill_id}/query",
        headers=headers,
        data=json.dumps(query_request),
    )

    response.raise_for_status()
    prediction_response = response.json()["predictions"]

    for datapoint, output in zip(dataset, prediction_response):
        predictions.append(
            Prediction(
                id=datapoint["id"],
                output=output["prediction_output"]["output"],
                output_score=output["prediction_output"]["output_score"],
            )
        )

    calculation_time = (datetime.datetime.now() - start_time).total_seconds()
    logger.info(f"Prediction finished after {calculation_time} seconds")

    prediction_result = PredictionResult(
        skill_id=ObjectId(skill_id),
        dataset_name=dataset_name,
        last_updated_at=datetime.datetime.now(),
        calculation_time=calculation_time,
        predictions=predictions,
    )

    mongo_client.client.evaluator.predictions.replace_one(
        {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name},
        prediction_result.dict(),
        upsert=True,
    )

    mongo_client.client.evaluator.evaluations.update_many(
        evaluation_filter,
        {
            "$set": {
                "prediction_status": EvaluationStatus.finished,
                "prediction_error": None,
            }
        },
    )

    # trigger evaluation task specified metric
    if metric_name is not None:
        mongo_client.client.evaluator.evaluations.update_many(
            evaluation_filter, {"$set": {"metric_status": EvaluationStatus.requested}}
        )
        task = evaluate_task.evaluate.apply_async(
            args=(skill_id, dataset_name, metric_name),
            task_id=task_id("evaluate", skill_id, dataset_name, metric_name),
        )
        logger.info(
            f"Created evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'. Task-ID: '{task.id}'"
        )
    else:
        logger.info(f"Not creating evaluation-task, because no metric was specified")

    prediction_result = prediction_result.dict()
    prediction_result["skill_id"] = skill_id
    prediction_result["predictions"] = (
        "List[" + str(len(prediction_result["predictions"])) + "]"
    )
    return prediction_result
