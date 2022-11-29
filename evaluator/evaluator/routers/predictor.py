import datetime
import json
import logging
from typing import Dict, List

import requests
from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator import mongo_client
from evaluator.core import DatasetHandler
from evaluator.core.dataset_handler import DatasetDoesNotExistError
from evaluator.models import Prediction, PredictionResult
from evaluator.routers import client_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predictor")
auth = Auth()


@router.post(
    "/{skill_id}/{dataset_name}",
    status_code=201,
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
    try:
        dataset = dataset_handler.get_dataset(dataset_name)
    except DatasetDoesNotExistError:
        logger.debug("Dataset does not exist!")
        raise HTTPException(400, "Dataset does not exist!")
    logger.debug(f"Dataset loaded: {dataset}")

    headers = {"Authorization": f"Bearer {token}"}
    if request.headers.get("Cache-Control"):
        headers["Cache-Control"] = request.headers.get("Cache-Control")

    predictions: List[Prediction] = []
    start_time = datetime.datetime.now()

    for i in range(8):
        reference_data = dataset[i]
        query_request = {
            "query": reference_data["question"],
            "skill_args": {"context": reference_data["context"]},
            "num_results": 1,
        }

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
    logger.debug(f"Prediction finished in {calculation_time} seconds: {predictions}")

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

    logger.info(f"Data saved in database")

    response.status_code = 201
    return prediction_result
