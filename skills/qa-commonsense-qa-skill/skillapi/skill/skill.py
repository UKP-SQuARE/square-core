import logging
import uuid

from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import ModelAPI

logger = logging.getLogger(__name__)

config = SquareSkillHelpersConfig.from_dotenv()
model_api = ModelAPI(config)

async def predict(request: QueryRequest) -> QueryOutput:
    """
    Process a given query and create the predictions for it.
    :param request: The user query
    :return: The prediction produced by the skill
    """

    choices = request.skill_args["context"].split("\n")

    # Call Model API
    prepared_input = [[request.query, c] for c in choices] 
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": "AdapterHub/bert-base-uncased-pf-commonsense_qa"
    }

    output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="sequence-classification", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{output}")

    # Prepare prediction
    query_output = []
    id2label = output["id2label"] # {'0': '', '1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E'}
    label2human_label = {id2label[str(i+1)]: c for i, c in enumerate(choices)}

    for i in range(len(choices)):
        logit = output["model_outputs"]["logits"][0][i]
        prediction_score = logit

        prediction_output = {
            "output": label2human_label[id2label[str(i+1)]],  # Set based on output
            "output_score": logit
        }

        prediction_documents = [{
            "index": "",
            "document_id": "",
            "document": "",
            # "span": ["", ""],
            "source": "",
            "url": ""
        }]  # Change as needed

        # Return
        prediction_id = str(uuid.uuid4())
        prediction = {
            "prediction_id": prediction_id,
            "prediction_score": prediction_score,
            "prediction_output": prediction_output,
            "prediction_documents": prediction_documents
        }
        query_output.append(prediction)

    query_output = sorted(query_output, key=lambda item: item["prediction_score"], reverse=True)

    return QueryOutput(predictions=query_output)
