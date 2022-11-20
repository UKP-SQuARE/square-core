import datetime
import logging
from typing import Dict, List
from bson import ObjectId

from evaluate import load
from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth
from square_auth.utils import is_local_deployment
from square_model_client import SQuAREModelClient

from evaluator import mongo_client
from evaluator.auth_utils import get_example_if_authorized
from evaluator.core import DatasetHandler
from evaluator.keycloak_api import KeycloakAPI
from evaluator.models import (
    DataPoint,
    DatasetResult,
    Example,
    Prediction,
    ReferenceAnswer,
)
from evaluator.routers import client_credentials

from evaluator.mongo.mongo_client import MongoClient


import requests
import json

import traceback
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluation")
auth = Auth()


@router.post(
    "/{skill_id}/{dataset_id}",
    status_code=200,
)
async def evaluation(
    request: Request,
    skill_id: str,
    dataset_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token: str = Depends(client_credentials),
    # To Do: Fix auth
    # token_payload: Dict = Depends(auth),
):
    dataset = dataset_handler.get_dataset(dataset_name)

    headers = {"Authorization": f"Bearer {token}"}
    if request.headers.get("Cache-Control"):
        headers["Cache-Control"] = request.headers.get("Cache-Control")

    logger.info(f"HEADERS: {headers}")

    data_points: List[DataPoint] = []

    for i in range(8):
        reference_data = dataset[i]
        query_request = {
            "query": reference_data["question"],
            "skill_args": {"context": reference_data["context"]},
            "num_results": 1,
        }

        logger.info(f"Running request {i}: {query_request}")
        response = requests.post(
            f"https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}/query",
            headers=headers,
            data=json.dumps(query_request),
        )

        prediction = response.json()["predictions"][0]

        logger.info(f"PREDICTION: {prediction}")

        data_points.append(
            DataPoint(
                id=reference_data["id"],
                context=reference_data["context"],
                question=reference_data["question"],
                reference_answers=ReferenceAnswer(
                    text=reference_data["answers"]["text"],
                    answer_start=reference_data["answers"]["answer_start"],
                ),
                prediction=Prediction(
                    text=prediction["prediction_output"]["output"],
                    no_answer_probability=1
                    - prediction["prediction_output"]["output_score"],
                ),
            )
        )

        logger.info(f"DATA POINT: {data_points[i]}")

    dataset_result = DatasetResult(
        skill_id=ObjectId(skill_id),
        dataset_name=dataset_name,
        dataset_last_updated_at=datetime.datetime.now(),
        data_points=data_points,
        metrics={},
    )

    mongo_client.client.evaluator.results.replace_one(
        {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name},
        dataset_result.dict(),
        upsert=True,
    )

    logger.info("DATA UPLOADED")

    # ---------------------------------------------------
    # To Do: Split Metric calculation into separate call!
    # ---------------------------------------------------

    metric_name = "squad_v2"
    metric = load(metric_name)
    identifier = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}

    loaded_data = DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(identifier)
    ).dict()

    logger.info("DATA LOADED")
    logger.info(loaded_data)

    references = [
        {
            "answers": {
                "text": d["reference_answers"]["text"],
                "answer_start": d["reference_answers"]["answer_start"],
            },
            "id": d["id"],
        }
        for d in loaded_data["data_points"]
    ]
    logger.info(f"REFERENCES: {references}")

    predictions = [
        {
            "prediction_text": d["prediction"]["text"],
            "no_answer_probability": d["prediction"]["no_answer_probability"],
            "id": d["id"],
        }
        for d in loaded_data["data_points"]
    ]
    logger.info(f"PREDICTIONS: {predictions}")

    m = metric.compute(predictions=predictions, references=references)

    new_metrics = loaded_data["metrics"]
    new_metrics[metric_name] = {"updated_at": datetime.datetime.now(), "results": m}
    mongo_client.client.evaluator.results.update_one(
        identifier,
        {"$set": {"metrics": new_metrics}},
    )

    logger.info(f"METRIC: {m}")

    return DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(identifier)
    )


# Old attempt: Remove later!


@router.post(
    "/old/{skill_id}/{dataset_id}",
    status_code=200,
)
async def evaluation_old(
    request: Request,
    skill_id: str,
    dataset_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
):
    dataset = dataset_handler.get_dataset("squad_v2")
    square_model_client = SQuAREModelClient()

    metric = load("squad_v2")

    model_request = {
        "input": [[dataset["question"][i], dataset["context"][i]] for i in range(8)],
        "task_kwargs": {"topk": 1},
        "adapter_name": "qa/squad2@ukp",
    }

    logger.info(f"MODEL REQUEST: {model_request}")
    logger.info("Lets start :)")
    for k, v in os.environ.items():
        logger.info(f" ENV: {k}={v}")
    try:
        model_api_output = await square_model_client(
            model_name="bert-base-uncased",
            pipeline="question-answering",
            model_request=model_request,
        )
        logger.info(f"MODEL OUTPUT: {model_api_output}")
        return model_api_output
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error("ERRRORRRRRR")
        logging.error(e)
        return e
