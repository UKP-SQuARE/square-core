import logging
import os
import requests
import numpy as np

from square_auth.client_credentials import ClientCredentials
from square_datastore_client import SQuAREDatastoreClient
from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest


logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """
    Given a question, calls the TWEAC model to identify the Skill to run.
    """
    logger.info("Request: {}".format(request))
    predicted_dataset = await _call_tweac(request)
    list_predicted_skills = await _retrieve_skills(predicted_dataset)
    skill_response = await _call_skill(list_predicted_skills[0], request)
    query_output = QueryOutput(
        predictions=skill_response.json()["predictions"],
        adversarial=skill_response.json()["adversarial"],
    )
    return query_output


async def _call_tweac(request):
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
    return dataset_name


async def _retrieve_skills(dataset_name):
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
        if skill["skill_type"] != "meta-skill"
    ]
    return list_predicted_skills


async def _call_skill(skill_id, request):
    skill_manager_api_url = os.getenv("SQUARE_API_URL") + "/skill-manager"
    client_credentials = ClientCredentials()
    token = client_credentials()

    input_data = {
        "query": request.query,
        "skill_args": {"context": request.skill_args["context"]},
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
