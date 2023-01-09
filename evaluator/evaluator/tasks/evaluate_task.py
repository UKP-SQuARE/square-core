import datetime
import json
import logging
from typing import Dict, List

import requests
from bson import ObjectId
from celery.utils.log import get_task_logger
from evaluate import load
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.core import DatasetHandler
from evaluator.app.core.dataset_handler import DatasetDoesNotExistError
from evaluator.app.core.metric_formatters import Formatter, MetricFormattingError
from evaluator.app.models import (
    Metric,
    MetricResult,
    Prediction,
    PredictionResult,
    get_dataset_metadata,
)
from evaluator.app.routers import client_credentials

from .celery import app as celery_app

logger = get_task_logger(__name__)


@celery_app.task
def evaluate(
    skill_id: str,
    dataset_name: str,
    metric_name: str,
):
    logger.info(
        f"Started evaluation-task for skill '{skill_id}' and dataset '{dataset_name}' on metric '{metric_name}'"
    )

    # Load the metric
    try:
        metric = load(metric_name)
    except FileNotFoundError:
        msg = f"Metric with name='{metric_name}' not found!"
        logger.error(msg)
        raise ValueError(msg)

    # Load the predictions for the given `skill_id` and `dataset_name`
    if hasattr(mongo_client, "client") == False:
        mongo_client.connect()
    try:
        prediction_result = PredictionResult.from_mongo(
            mongo_client.client.evaluator.predictions.find_one(
                {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}
            )
        )
        if prediction_result is None:
            raise AttributeError
    except AttributeError as e:
        msg = f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!"
        logger.error(msg)
        raise ValueError(msg)

    # Load dataset metadata (TODO)
    dataset_metadata = get_dataset_metadata(dataset_name)

    # Load the dataset
    dataset_handler = DatasetHandler()
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError as e:
        logger.error(f"{e}")
        raise e

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
        raise e

    # map references into correct format (from generic dataset format to metric format)
    try:
        references = Formatter().format_references(metric_name, references)
    except MetricFormattingError as e:
        logger.error(f"{e}")
        raise ValueError(
            f"The dataset '{dataset_name}' cannot be evaluated on metric '{metric_name}'."
        )

    # calculate metric
    start_time = datetime.datetime.now()
    try:
        m = metric.compute(predictions=predictions, references=references)
    except ValueError as e:
        msg = f"Could not evaluate metric '{metric_name}' on dataset '{dataset_name}': {e}"
        logger.error(msg)
        raise ValueError(msg)
    calculation_time = (datetime.datetime.now() - start_time).total_seconds()

    # save metric results in database
    metric_result_identifier = {"prediction_result_id": prediction_result.id}
    metric_result = MetricResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(metric_result_identifier)
    )
    if metric_result is None:
        metric_result = MetricResult(
            prediction_result_id=prediction_result.id, metrics={}
        )

    metric = Metric(
        last_updated_at=datetime.datetime.now(),
        calculation_time=calculation_time,
        results=m,
    )
    new_metrics = metric_result.metrics
    new_metrics[metric_name] = metric

    mongo_client.client.evaluator.results.replace_one(
        metric_result_identifier, metric_result.mongo(), upsert=True
    )

    logger.info(f"New metric result: {metric_result}")
    return metric_result.metrics[metric_name].dict()
