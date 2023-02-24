import logging
import os
from concurrent.futures import ThreadPoolExecutor

import requests

from square_auth.client_credentials import ClientCredentials
from square_model_client import SQuAREModelClient
from square_skill_api.models import (
    Prediction,
    PredictionOutput,
    QueryOutput,
    QueryRequest,
)

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
client_credentials = ClientCredentials()


def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and (context), (answer),
    it calls the Skill agents to get the predictions,
    and then calls MetaQA Model to get the final prediction.
    """
    list_skills = request.skill_args["list_skills"]

    # 1) call the skills in parallel
    list_skill_responses = _call_skills(list_skills, request)
    # 2) prepare MetaQA input
    qa_format = _get_qa_format(request)
    if qa_format == "span-extraction":
        model_request = _create_metaqa_request_for_span_extraction(
            request, list_skill_responses
        )
    elif qa_format == "multiple-choice":
        model_request = _create_metaqa_request_for_multiple_choice(
            request, list_skill_responses
        )
    else:
        # raise error
        logger.info(f"Unsopported Skill Type:\n{qa_format}")
    # 3) Call MetaQA Model API
    model_response = square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")
    # 4) Prepare MetaQA output
    return _create_metaqa_output(request, model_response)


def _get_qa_format(request):
    return request.skill["skill_type"]


def _call_skills(list_skills, request):
    """
    Calls the skills in parallel
    """
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        list_skill_responses = executor.map(
            _call_skill, list_skills, [request] * len(list_skills)
        )

    return list_skill_responses


def _call_skill(skill_id, request):
    token = client_credentials()

    input_data = {
        "query": request.query,
        "skill_args": {
            "context": request.skill_args["context"]
            if "context" in request.skill_args
            else "",
            "choices": request.skill_args["choices"]
            if "choices" in request.skill_args
            else [],
        },
        "skill": {},
        "user_id": "",
        **extract_model_kwargs_from_request(request),
    }
    # skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    logger.debug(f"Calling skill {skill_id}.")
    response = requests.post(
        url="http://skill-manager:8000/api/skill/" + skill_id + "/query",
        json=input_data,
        headers={"Content-Type": "application/json"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    response.raise_for_status()
    result = response.json()
    logger.debug(f"Skill {skill_id} responded.")

    return result


def _create_metaqa_request_for_span_extraction(request, list_skill_responses):
    list_preds = [["", 0.0]] * 16
    for skill_idx, skill_response in enumerate(list_skill_responses):
        pred = skill_response["predictions"][0]["prediction_output"]["output"]
        score = skill_response["predictions"][0]["prediction_output"]["output_score"]
        list_preds[skill_idx] = (pred, score)

    model_request = {
        "input": {
            "question": request.query,
            "agents_predictions": list_preds,
        },
        "task_kwargs": {"topk": request.task_kwargs.get("topk", 1)},
    }

    return model_request


def _create_metaqa_request_for_multiple_choice(request, list_skill_responses):
    list_preds = [("", 0.0)] * 16
    for skill_idx, skill_response in enumerate(list_skill_responses):
        pred = skill_response["predictions"][0]["prediction_output"]["output"]
        score = skill_response["predictions"][0]["prediction_output"]["output_score"]
        list_preds[8 + skill_idx] = (pred, score)

    model_request = {
        "input": {
            "question": request.query,
            "agents_predictions": list_preds,
        },
        "task_kwargs": {"topk": request.task_kwargs.get("topk", 1)},
    }

    return model_request


def _create_metaqa_output(request, model_response):
    list_predictions = []
    for answer in model_response["answers"][0]:
        list_predictions.append(
            Prediction(
                question=request.query,
                prediction_score=answer["metaqa_score"],
                prediction_output=PredictionOutput(
                    output=answer["answer"], output_score=answer["agent_score"]
                ),
                skill_id=answer["agent_name"],
            )
        )
    return QueryOutput(predictions=list_predictions)
