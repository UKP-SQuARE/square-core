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

from evaluator import mongo_client
from evaluator.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.core.metric_formatters import Formatter, MetricFormattingError
from evaluator.models import (
    ExtractiveDatasetSample,
    Metric,
    MetricResult,
    MultipleChoiceDatasetSample,
    PredictionResult,
)
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

    # map predictions into correct format (from skill output format to metric format)
    predictions, sample_ids = Formatter().format_predictions(
        metric_name, prediction_result.predictions
    )

    # map the dataset into a generic format
    try:
        references = dataset_handler.to_generic_format(
            dataset, dataset_metadata, sample_ids
        )
    except ValueError as e:
        logger.error(f"{e}")
        raise HTTPException(400, f"{e}")

    # map references into correct format (from generic dataset format to metric format)
    try:
        references = Formatter().format_references(metric_name, references)
    except MetricFormattingError as e:
        logger.error(f"{e}")
        raise HTTPException(
            400,
            f"The dataset '{dataset_name}' cannot be evaluated on metric '{metric_name}'.",
        )

    # Execute metric
    start_time = datetime.datetime.now()
    try:
        m = metric.compute(predictions=predictions, references=references)
    except ValueError as e:
        msg = f"Could not evaluate metric '{metric_name}' on dataset '{dataset_name}': {e}"
        logger.error(msg)
        raise HTTPException(400, msg)

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

    return metric


def get_dataset_metadata(dataset_name):
    if dataset_name == "squad":
        return {
            "name": "squad",
            "skill-type": "extractive-qa",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
            },
        }
    elif dataset_name == "quoref":
        return {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
            },
        }
    elif dataset_name == "commonsense_qa":
        return {
            "name": "commonsense_qa",
            "skill-type": "multiple-choice",
            "metric": "accuracy",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "choices-columns": ["choices.text"],
                "choices-key-mapping-column": "choices.label",
                "answer-index-column": "answerKey",
            },
        }
    elif dataset_name == "cosmos_qa":
        return {
            "name": "cosmos_qa",
            "skill-type": "multiple-choice",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "choices-columns": ["answer0", "answer1", "answer2", "answer3"],
                "choices-key-mapping-column": None,
                "answer-index-column": "label",
            },
        }
    else:
        logger.error("Unsupported dataset!")
        raise HTTPException(400, "Unsupported dataset!")
