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
from evaluator.models import (
    ExtractiveDatasetSample,
    ExtractiveDatasetSampleAnswer,
    Metric,
    MetricResult,
    PredictionResult,
)
from evaluator.prediction_formatters import PredictionFormatter
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
    # if metric_name != "squad":
    #    logger.error("Unsupported metric name!")
    #    raise HTTPException(400, "Sorry, we currently only support the metric 'squad'!")

    object_identifier = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}

    # Load the metric from HuggingFace
    try:
        metric = load(metric_name)
    except FileNotFoundError:
        logger.error(f"Metric with name='{metric_name}' not found!")
        raise HTTPException(404, f"Metric with name='{metric_name}' not found!")

    # Load the predictions for the given `skill_id` and `dataset_name` from MongoDB
    prediction_result = PredictionResult.from_mongo(
        mongo_client.client.evaluator.predictions.find_one(object_identifier)
    )
    if prediction_result is None:
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
    predictions, sample_ids = PredictionFormatter().format(
        metric_name, prediction_result.predictions
    )
    logger.debug(f"Predictions formatted for metric: {predictions}")
    logger.debug(f"Sample-IDs: {sample_ids}")

    references = format_references(metric_name, dataset_metadata, dataset, sample_ids)
    # We need to parse the references into metric format
    """references = [
        {"answers": sample["answers"], "id": sample["id"]}
        for sample in dataset
        if sample["id"] in sample_ids
    ]"""

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


def format_references(metric_name, dataset_metadata, dataset, sample_ids):
    if dataset_metadata["skill-type"] not in ["extractive-qa", "multiple-choice"]:
        skill_type = dataset_metadata["skill-type"]
        raise HTTPException(
            400, f"Evaluation of '{skill_type}' datasets is currently not supported."
        )

    if dataset_metadata["skill-type"] == "extractive-qa":
        dataset = map_extractive_dataset(dataset_metadata, dataset)
    elif dataset_metadata["skill-type"] == "multiple-choice":
        dataset = dataset.map(quail_map)

    return [
        dataset[0],
        dataset[1],
        dataset[2],
        dataset[3],
        dataset[4],
        dataset[5],
        dataset[6],
        dataset[7],
    ]


def map_extractive_dataset(dataset_metadata, dataset):
    samples = []
    for sample in dataset:
        attrs = dataset_metadata["mapping"]["answer-text-column"].split(".")
        answer_texts = sample[attrs[0]]
        if len(attrs) > 1:
            answer_texts = sample[attrs[0]][attrs[1]]

        try:
            attrs = dataset_metadata["mapping"]["answer-start-column"].split(".")
            answer_starts = sample[attrs[0]]
            if len(attrs) > 1:
                answer_starts = sample[attrs[0]][attrs[1]]
        except KeyError:
            answer_starts = False

        formatted_answers = []
        for answer_index, _ in enumerate(answer_texts):
            if not answer_starts:
                start = sample[dataset_metadata["mapping"]["context-column"]].index(
                    answer_texts[answer_index]
                )
            else:
                start = answer_starts[answer_index]
            a = ExtractiveDatasetSampleAnswer(
                text=answer_texts[answer_index], answer_start=start
            )
            formatted_answers.append(a)

        d = ExtractiveDatasetSample(
            id=sample[dataset_metadata["mapping"]["id-column"]],
            answers=formatted_answers,
        )

        logger.debug(f"Formatted extractive-qa sample {d.dict()}")
        samples.append(d.dict())
    return samples


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
                "answer-start-column": "answers.answer_start",
            },
        }
    elif dataset_name == "quoref":
        return {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
                "answer-start-column": "answers.answer_start",
            },
        }
    else:
        logger.error("Unsupported dataset!!!!!")
        raise HTTPException(400, "Unsupported dataset!!!!!")
