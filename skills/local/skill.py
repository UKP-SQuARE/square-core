import logging

from square_datastore_client import SQuAREDatastoreClient
from square_model_client import SQuAREModelClient
from square_skill_api.models import (
    Prediction,
    PredictionOutput,
    QueryOutput,
    QueryRequest,
)

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:

    """
    Given a question, calls the TWEAC model to identify the Skill to run.
    """
    query = request.query

    # Call Model API
    model_request = {
        "input": [query],
    }

    logger.debug("Request for model api:{}".format(model_request))

    # model_response = await square_model_client(
    #     model_name=request.skill_args["base_model"],
    #     pipeline="sequence-classification",
    #     model_request=model_request,
    # )
    model_response = {'model_outputs': {'logits': None},
                      'model_output_is_encoded': True,
                      'labels': [0],
                      'id2label': {0: 'LABEL_0', 1: 'LABEL_1', 10: 'LABEL_10', 11: 'LABEL_11', 12: 'LABEL_12', 13: 'LABEL_13', 14: 'LABEL_14', 15: 'LABEL_15', 2: 'LABEL_2', 3: 'LABEL_3', 4: 'LABEL_4', 5: 'LABEL_5', 6: 'LABEL_6', 7: 'LABEL_7', 8: 'LABEL_8', 9: 'LABEL_9'},
                      'attributions': [],
                      'questions': [],
                      'contexts': [],
                      'adversarial': {}
                      }
    logger.info("Model response: {}".format(model_response))
        
    raw_pred = model_response["labels"][0]
    # dataset_name = model_response["labels"][0]
    # score = model_response["model_outputs"]["logits"][0]
    logger.info("Raw prediction: {}".format(raw_pred))
    dataset_name = model_response['id2label'][raw_pred]
    logger.info("TWEAC prediction: {}".format(dataset_name))
    
    return QueryOutput(
        predictions=[
            Prediction(
                question="What is the capital of France?",
                prediction_score=0.9,
                prediction_output=PredictionOutput(output=dataset_name, output_score=0.9),
            )
        ]
    )
    
    # # API call to Skill Manager to get the names of the skills trained on the dataset
    # skill_manager_api_url = os.getenv("SQUARE_SKILL_MANAGER")
    # logger.info("Skill Manager API URL: {}".format(skill_manager_api_url))
    # client_credentials = ClientCredentials()
    # response = requests.get(
    #         url=f"{skill_manager_api_url}/dataset/{dataset_name}",
    #         headers={"Authorization": f"Bearer {client_credentials}"},
    #         verify=os.getenv("VERIFY_SSL") == "1",
    #     )
    # list_skills = response.json()
    # list_skill_ids = [skill["id"] for skill in list_skills]
    
    # return list_skill_ids
    # pred_output = PredictionOutput(output="", output_score=0.0)
    # return QueryOutput(predictions=[Prediction(question="foo", prediction_score=0.0, prediction_output=pred_output)])

