import asyncio
import logging
import os

import numpy as np
import requests
from square_auth.client_credentials import ClientCredentials
from square_datastore_client import SQuAREDatastoreClient
from square_model_client import SQuAREModelClient
from square_skill_api.models import (
    QueryOutput,
    QueryRequest,
    Prediction,
    PredictionOutput,
)

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """
    Given a question, calls the TWEAC model to identify the Skill to run.
    """
    logger.info("Request: {}".format(request))
    qa_format = _get_qa_format(request)

    predicted_dataset, tweac_conf = await _call_tweac(request)
    list_predicted_skills = await _retrieve_skills(predicted_dataset, qa_format)
    if len(list_predicted_skills) == 0:
        return _create_no_skill_response(request.query)

    list_predicted_skills = list_predicted_skills[
        : request.skill_args["max_skills_per_dataset"]
    ]
    list_skill_responses = await _call_skills(list_predicted_skills, request)

    list_predictions = []
    for skill_id, skill_response in zip(list_predicted_skills, list_skill_responses):
        predictions = skill_response.json()["predictions"]
        # add skill_id and confidence to the prediction
        pred = predictions[0]
        pred["skill_id"] = skill_id
        pred["prediction_score"] = (
            pred["prediction_output"]["output_score"] * tweac_conf
        )
        list_predictions.append(pred)

    query_output = QueryOutput(
        predictions=list_predictions,
        adversarial=[],
    )

    return query_output


async def _call_tweac(request):
    """
    Calls the TWEAC model and returns the predicted dataset and confidence score
    """
    model_request = {
        "input": [request.query],
    }
    logger.debug("Request for model api:{}".format(model_request))

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info("TWEAC response: {}".format(model_response))
    # get top 1 prediction
    raw_pred = model_response["labels"][0]
    logger.info("Raw prediction: {}".format(raw_pred))
    dataset_name = model_response["id2label"][str(raw_pred)]
    logger.info("TWEAC prediction: {}".format(dataset_name))
    conf = model_response["model_outputs"]["logits"][0][raw_pred]
    return dataset_name, conf


async def _retrieve_skills(dataset_name, qa_format):
    """
    API call to Skill Manager to get the names of the skills trained on the dataset
    """
    skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    client_credentials = ClientCredentials()
    token = client_credentials()
    api_call = f"{skill_manager_api_url}/skill/dataset/{dataset_name}"
    logger.info("Calling: {}".format(api_call))
    response = requests.get(
        url=f"{skill_manager_api_url}/skill/dataset/{dataset_name}",
        headers={"Authorization": f"Bearer {token}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    logger.info("Retrieved Skills: {}".format(response))
    list_predicted_skills = response.json()

    list_predicted_skills = [
        skill["id"]
        for skill in list_predicted_skills
        if (not skill["meta_skill"]) and (skill["skill_type"] == qa_format)
    ]
    return list_predicted_skills


async def _call_skills(list_predicted_skills, request):
    """
    Calls the skills in parallel
    """
    list_skill_responses = []
    for skill_id in list_predicted_skills:
        # how to call the skill without waiting
        skill_response = _call_skill(skill_id, request)  # only 1 answer per skill
        list_skill_responses.append(skill_response)
    list_skill_responses = await asyncio.gather(*list_skill_responses)
    return list_skill_responses


async def _call_skill(skill_id, request):
    skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    client_credentials = ClientCredentials()
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
    return response


def _get_qa_format(request):
    return request.skill["skill_type"]


def _create_no_skill_response(question):
    """
    Creates a response when no skill is found
    """
    return QueryOutput(
        predictions=[
            Prediction(
                question=question,
                prediction_score=0.0,
                prediction_output=PredictionOutput(
                    output="No answer found.", output_score=0.0
                ),
            )
        ],
    )
