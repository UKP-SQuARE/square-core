import datetime
import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from square_auth.auth import Auth

from evaluator import mongo_client
from evaluator.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.models import Metric, MetricResult, PredictionResult
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
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    _token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"start evaluation with parameters: skill_id={skill_id}; dataset_name={dataset_name}; metric_name={metric_name}"
    )

    # ToDo: Add support for other metrics
    if metric_name != "squad":
        logger.error("Unsupported metric name!")
        raise HTTPException(400, "Sorry, we currently only support the metric 'squad'!")

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
        logger.debug(f"Prediction loaded: {prediction_result}")
    except AttributeError:
        msg = f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!"
        logger.error(msg)
        raise HTTPException(404, msg)

    # Load the dataset from DatasetHandler
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.error("Dataset does not exist!")
        raise HTTPException(400, "Dataset does not exist!")

    # We need to parse the predictions into metric format
    predictions = [
        {
            "id": pr.id,
            "prediction_text": pr.output,
        }
        for pr in prediction_result.predictions
    ]

    # Convert all prediction ids into set
    prediction_ids = set([x["id"] for x in predictions])

    # We need to parse the references into metric format
    references = [
        {"answers": d["answers"], "id": d["id"]}
        for d in dataset
        if d["id"] in prediction_ids
    ]

    # Execute metric
    start_time = datetime.datetime.now()
    m = metric.compute(predictions=predictions, references=references)
    calculation_time = (datetime.datetime.now() - start_time).total_seconds()

    metric_result_identifier = {"prediction_result_id": prediction_result.id}
    metric_result = MetricResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(metric_result_identifier)
    )
    if metric_result is None:
        logger.debug(f"No metric result found. Creating new one.")
        metric_result = MetricResult(
            prediction_result_id=prediction_result.id, metrics={}
        )
    else:
        logger.debug(f"Existing metric result loaded: {metric_result}")

    metric = Metric(
        last_updated_at=datetime.datetime.now(),
        calculation_time=calculation_time,
        results=m,
    )
    new_metrics = metric_result.metrics
    new_metrics[metric_name] = metric

    logger.info(f"New Metric Result: {metric_result}")

    mongo_client.client.evaluator.results.replace_one(
        metric_result_identifier, metric_result.mongo(), upsert=True
    )

    return metric_result
