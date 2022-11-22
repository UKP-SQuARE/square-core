import datetime
import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator import mongo_client
from evaluator.models import DatasetResult, Metric
from evaluator.routers import client_credentials

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
    _token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"start evaluation with parameters: skill_id={skill_id}; dataset_name={dataset_name}; metric_name={metric_name}"
    )

    if metric_name != "squad_v2":
        logger.debug("Unsupported metric name!")
        raise HTTPException(
            400, "Sorry, we currently only support the metric 'squad_v2'!"
        )

    object_identifier = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}

    try:
        metric = load(metric_name)
    except FileNotFoundError:
        logger.debug(f"Metric with name='{metric_name}' not found!")
        raise HTTPException(404, f"Metric with name='{metric_name}' not found!")

    try:
        loaded_data = DatasetResult.from_mongo(
            mongo_client.client.evaluator.results.find_one(object_identifier)
        ).dict()
        logger.debug(f"Data loaded: {loaded_data}")
    except AttributeError:
        logger.debug(
            f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!"
        )
        raise HTTPException(
            404,
            f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!",
        )

    references = [
        {
            "answers": {
                "text": d["reference_answers"]["text"],
                "answer_start": d["reference_answers"]["answer_start"],
            },
            "id": d["id"],
        }
        for d in loaded_data["predictions"]
    ]
    logger.debug(f"Parsed references: {references}")

    predictions = [
        {
            "prediction_text": d["prediction"]["text"],
            "no_answer_probability": d["prediction"]["no_answer_probability"],
            "id": d["id"],
        }
        for d in loaded_data["predictions"]
    ]
    logger.debug(f"Parsed predictions: {predictions}")

    start_time = datetime.datetime.now()
    m = metric.compute(predictions=predictions, references=references)
    calculation_time = (datetime.datetime.now() - start_time).total_seconds()

    logger.debug(f"Metric in {calculation_time} seconds calculated: {m}")

    new_metrics = loaded_data["metrics"]
    new_metrics[metric_name] = Metric(
        metric_last_updated_at=datetime.datetime.now(),
        metric_calculation_time=calculation_time,
        results=m,
    ).dict()

    mongo_client.client.evaluator.results.update_one(
        object_identifier,
        {"$set": {"metrics": new_metrics}},
    )

    return DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(object_identifier)
    )
