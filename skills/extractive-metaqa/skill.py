import asyncio
import logging
import os
import time

import aiohttp
from square_model_client import SQuAREModelClient
from square_skill_api.models import (
    Prediction,
    PredictionOutput,
    QueryOutput,
    QueryRequest,
)

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and (context), (answer),
    it calls the Skill agents to get the predictions,
    and then calls MetaQA Model to get the final prediction.
    """
    query = request.query
    list_skills = request.skill_args["list_skills"]

    # 1) call the skills in parallel
    list_skill_responses = await _call_skills(list_skills, request)
    # 2) get the predictions
    list_preds = [["", 0.0]] * 16
    for skill_idx, skill_response in enumerate(list_skill_responses):
        pred = skill_response["predictions"][0]["prediction_output"]["output"]
        score = skill_response["predictions"][0]["prediction_output"]["output_score"]
        list_preds[skill_idx] = (pred, score)

    # 4) Call MetaQA Model API
    model_request = {
        "input": {
            "question": query,
            "agents_predictions": list_preds,
        },
        "task_kwargs": {"topk": request.task_kwargs.get("topk", 1)},
    }

    model_response = await square_model_client(
        model_name="metaqa",
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return _create_metaqa_output_from_question_answering(request, model_response)


async def _call_skills(list_skills, request):
    """
    Calls the skills in parallel
    """
    t1 = time.time()
    list_skill_responses = []
    for skill_id in list_skills:
        # how to call the skill without waiting
        skill_response = _call_skill(skill_id, request)  # only 1 answer per skill
        list_skill_responses.append(skill_response)
    list_skill_responses = await asyncio.gather(*list_skill_responses)
    t2 = time.time()
    logger.info(f"TOTAL TIME={t2-t1:.2f}")
    return list_skill_responses


async def _call_skill(skill_id, request):
    t1 = time.time()
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
        "explain_kwargs": request.explain_kwargs or {},
        "attack_kwargs": request.attack_kwargs or {},
        "model_kwargs": request.model_kwargs or {},
        "task_kwargs": request.task_kwargs or {},
        "preprocessing_kwargs": request.preprocessing_kwargs or {},
    }
    # skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url="http://skill-manager:8000/api/skill/" + skill_id + "/query",
            json=input_data,
            headers={"Content-Type": "application/json"},
            verify_ssl=os.getenv("VERIFY_SSL") == "1",
        ) as response:
            response.raise_for_status()
            result = await response.json()
            t2 = time.time()
            logger.info(f"TIME={t2-t1:.2f} skill_id={skill_id}")
            return result


def _create_metaqa_output_from_question_answering(request, model_response):
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
