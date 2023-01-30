import logging
import os
import requests
import asyncio

from square_skill_api.models import QueryOutput, QueryRequest
from square_model_client import SQuAREModelClient
from square_auth.client_credentials import ClientCredentials

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
client_credentials = ClientCredentials()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and (context), (answer),
    it calls the Skill agents to get the predictions,
    and then calls MetaQA Model to get the final prediction.
    """
    task_dict_skill_id2skill_type = asyncio.create_task(_get_skill_types())
    list_skills = request.skill_args["list_skills"]

    query = request.query
    qa_format = _get_qa_format(request)

    # 1) get the skills we can use for this question
    list_valid_skills = []
    list_idx_valid_skills = []
    dict_skill_id2skill_type = await task_dict_skill_id2skill_type
    for skill_idx, skill_id in enumerate(list_skills):
        skill_type = dict_skill_id2skill_type[skill_id]
        if qa_format == skill_type:
            list_valid_skills.append(skill_id)
            list_idx_valid_skills.append(skill_idx)

    # 2) call the skills in parallel
    list_skill_responses = await _call_skills(list_valid_skills, request)
    # 3) get the predictions
    list_preds = [("", 0.0)] * len(list_skills)
    for (skill_idx, skill_response) in zip(list_idx_valid_skills, list_skill_responses):
        pred = skill_response["predictions"][0]["prediction_output"]["output"]
        score = skill_response["predictions"][0]["prediction_output"]["output_score"]
        list_preds[skill_idx] = (pred, score)

    # 4) Call MetaQA Model API
    model_request = {
        "input": [[query, list_preds]],
    }

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return _prepare_output(request, model_response)


def _get_qa_format(request):
    return request.skill["skill_type"]


async def _get_skill_types():
    skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    token = client_credentials()
    response = requests.get(
        url=skill_manager_api_url + "/skill",
        headers={"Authorization": f"Bearer {token}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    return {skill["id"]: skill["skill_type"] for skill in response.json()}


async def _call_skills(list_skills, request):
    """
    Calls the skills in parallel
    """
    list_skill_responses = []
    for skill_id in list_skills:
        # how to call the skill without waiting
        skill_response = _call_skill(skill_id, request)  # only 1 answer per skill
        list_skill_responses.append(skill_response)
    list_skill_responses = await asyncio.gather(*list_skill_responses)
    return list_skill_responses


async def _call_skill(skill_id, request):
    skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
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
        "explain_kwargs": {},
    }

    response = requests.post(
        url=skill_manager_api_url + "/skill/" + skill_id + "/query",
        json=input_data,
        headers={"Authorization": f"Bearer {token}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    return response.json()


def _prepare_output(request, model_response):
    if _get_qa_format(request) == "span-extraction":
        return QueryOutput.from_question_answering(
            questions=request.query,
            model_api_output=model_response,
            context=request.skill_args["context"],
        )
    elif _get_qa_format(request) == "multiple-choice":
        return QueryOutput.from_sequence_classification(
            questions=request.query,
            answers=request.skill_args["choices"],
            model_api_output=model_response,
            context=request.skill_args["context"],
        )
