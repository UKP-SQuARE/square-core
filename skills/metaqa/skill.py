import logging
import os
import requests

from square_skill_api.models import QueryOutput, QueryRequest
from square_model_client import SQuAREModelClient
from square_auth.client_credentials import ClientCredentials

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and (context), (answer),
    it calls the Skill agents to get the predictions,
    and then calls MetaQA Model to get the final prediction.
    """    
    list_skills = request.skill_args["list_skills"]
    
    query = request.query
    context = request.skill_args["context"]
    choices = request.skill_args["choices"]
    
    skill_type = request.skill.get("skill_type")
    
    # get predictions from Skill agents
    list_preds = [] # each item is (prediction, confidence)
    for skill_id in list_skills:
        if skill_type == _get_skill_type(skill_id):
            response = _call_skill(skill_id, query, context, choices)
            pred = response.predictions[0].prediction_output.output
            score = response.predictions[0].prediction_output.output_score
            list_preds.append((pred, score))
        else:
            list_preds.append(("", 0.0))
        
    # Call MetaQA Model API
    model_request = {
        "input": [[query, list_preds]],
    }

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_question_answering(
        questions=query, model_api_output=model_response, context=context
    )
    
async def _get_skill_type(skill_id):
    skill_manager_api_url = os.getenv("SQUARE_SKILL_MANAGER")
    client_credentials = ClientCredentials()
    
    response = requests.get(
        url=skill_manager_api_url + "/skill/" + skill_id,
        headers={"Authorization": f"Bearer {client_credentials}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    return response.jons()['skill_type']    

async def _call_skill(skill_id, question, context, choices):
    # skill_manager_api_url = "https://square.ukp-lab.de/api/skill-manager"
    skill_manager_api_url = os.getenv("SQUARE_SKILL_MANAGER")
    client_credentials = ClientCredentials()
    # client_credentials = "TOKEN"

    input_data = {
        "query": question,
        "skill_args": {},
    }
    
    if context is not None:
        input_data["skill_args"]["context"] = context
    if choices is not None:
        input_data["skill_args"]["choices"] = choices

    response = requests.post(
        url=skill_manager_api_url + "/skill/" + skill_id + "/query",
        json=input_data,
        headers={"Authorization": f"Bearer {client_credentials}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    return response

