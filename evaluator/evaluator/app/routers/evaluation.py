import logging
from typing import Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.auth_utils import (
    get_payload_from_token,
    has_auth_header,
    validate_access,
)
from evaluator.app.core.evaluation_handler import EvaluationHandler
from evaluator.app.models import (
    Evaluation,
    EvaluationResult,
    EvaluationStatus,
    MetricResult,
)
from evaluator.app.routers import client_credentials
from evaluator.app.routers.router_utils.router_utils import get_skills

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
        return evaluation_handler.evaluate(
            user_id, token, skill_id, dataset_name, metric_name
        )
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
        return evaluation_handler.evaluate(user_id, token, skill_id, dataset_name, None)
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
        return evaluation_handler.compute_metric(
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
        return evaluation_handler.do_predictions(user_id, token, skill_id, dataset_name)
    except Exception as e:
        raise HTTPException(400, f"{e}")


@router.get(
    "/evaluations",
    response_model=List[EvaluationResult],
)
async def get_evaluations(request: Request, token: str = Depends(client_credentials)):
    """Returns all evaluations that a user has access to. A user has access to
    all public evaluations, and private evaluations created by them."""

    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]

    metric_results = mongo_client.client.evaluator.results.find()
    metric_results = [MetricResult.from_mongo(e) for e in metric_results]
    results = []

    evaluations = mongo_client.client.evaluator.evaluations.find()
    evaluations = [Evaluation.from_mongo(e) for e in evaluations]

    skills = get_skills(token)

    for evaluation in evaluations:
        skill_id = str(evaluation.skill_id)

        if not skill_id in skills:
            continue

        skill_is_public = skills[skill_id]["published"]
        has_access = skill_is_public or skills[skill_id]["user_id"] == user_id

        if not has_access:
            continue

        if (
            evaluation.prediction_status is not EvaluationStatus.finished
            or evaluation.metric_status is not EvaluationStatus.finished
        ):
            if (
                evaluation.prediction_status is EvaluationStatus.failed
                or evaluation.metric_status is EvaluationStatus.failed
            ):
                status = "FAILED"
                error = (
                    evaluation.prediction_error
                    if evaluation.prediction_status == EvaluationStatus.failed
                    else evaluation.metric_error
                )
            else:
                status = "RUNNING"

            results.append(
                EvaluationResult(
                    evaluation_id=str(evaluation.id),
                    evaluation_status=status,
                    evaluation_error=error,
                    skill_name=skills[skill_id]["name"],
                    dataset=evaluation.dataset_name,
                    public=skill_is_public,
                    metric_name=evaluation.metric_name,
                    metric_result=[],
                    skill_url=skills[skill_id]["url"],
                )
            )
            continue

        status = "FINISHED"
        metric_result = next(
            item
            for item in metric_results
            if str(item.skill_id) == skill_id
            and item.dataset_name == evaluation.dataset_name
        )

        for (metric_name, metric_data) in metric_result.metrics.items():
            if metric_name == evaluation.metric_name:
                results.append(
                    EvaluationResult(
                        evaluation_id=str(evaluation.id),
                        evaluation_status=status,
                        evaluation_error="",
                        skill_name=skills[skill_id]["name"],
                        dataset=metric_result.dataset_name,
                        public=skill_is_public,
                        metric_name=metric_name,
                        metric_result=metric_data["results"],
                        skill_url=skills[skill_id]["url"],
                    )
                )

    return results


@router.delete("/delete_evaluation/{skill_id}/{dataset_name}/{metric_name}")
async def delete_evaluation(
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    token_payload: Dict = Depends(auth),
):
    """Deletes an evaluation"""
    validate_access(token_payload)
    logger.debug(f"Deleting evaluation with id: {id}")

    delete_result = mongo_client.client.evaluator.evaluations.delete_one(
        {
            "skill_id": ObjectId(skill_id),
            "dataset_name": dataset_name,
            "metric_name": metric_name,
        }
    )

    if delete_result.deleted_count == 1:
        logger.info(f"Evaluation with skill id={id} successfully deleted.")
        return
    else:
        message = f"Evaluation with skill id {id} could not be deleted, because it was not found."
        logger.warning(message)
        raise HTTPException(404, message)
