import datetime
import logging
from typing import Dict

import requests
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator.app.core.evaluation_handler import EvaluationHandler
from evaluator.app.routers import client_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="")
auth = Auth()


@router.post(
    "/evaluate/{skill_id}/{dataset_name}/{metric_name}",
    status_code=202,
)
async def evaluate(
    request: Request,
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    evaluation_handler: EvaluationHandler = Depends(EvaluationHandler),
    token: str = Depends(client_credentials),
    token_payload: Dict = Depends(auth),
):
    user_id = token_payload["username"]
    try:
        evaluation_handler.evaluate(user_id, token, skill_id, dataset_name, metric_name)
    except Exception as e:
        raise HTTPException(400, f"{e}")


@router.post(
    "/evaluate/{skill_id}/{dataset_name}",
    status_code=202,
)
async def evaluate(
    request: Request,
    skill_id: str,
    dataset_name: str,
    evaluation_handler: EvaluationHandler = Depends(EvaluationHandler),
    token: str = Depends(client_credentials),
    token_payload: Dict = Depends(auth),
):
    user_id = token_payload["username"]
    try:
        evaluation_handler.evaluate(user_id, token, skill_id, dataset_name, None)
    except Exception as e:
        raise HTTPException(400, f"{e}")


@router.post(
    "/compute-metric/{skill_id}/{dataset_name}/{metric_name}",
    status_code=202,
)
async def compute_metric(
    request: Request,
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    evaluation_handler: EvaluationHandler = Depends(EvaluationHandler),
    token: str = Depends(client_credentials),
    token_payload: Dict = Depends(auth),
):
    user_id = token_payload["username"]
    try:
        evaluation_handler.compute_metric(
            user_id, token, skill_id, dataset_name, metric_name
        )
    except Exception as e:
        raise HTTPException(400, f"{e}")


@router.post(
    "/compute-predictions/{skill_id}/{dataset_name}",
    status_code=202,
)
async def compute_predictions(
    request: Request,
    skill_id: str,
    dataset_name: str,
    evaluation_handler: EvaluationHandler = Depends(EvaluationHandler),
    token: str = Depends(client_credentials),
    token_payload: Dict = Depends(auth),
):
    user_id = token_payload["username"]
    try:
        evaluation_handler.do_predictions(user_id, token, skill_id, dataset_name)
    except Exception as e:
        raise HTTPException(400, f"{e}")
