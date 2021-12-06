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

    # Call Model API
    query = request.query
    context = request.skill_args.context
    prepared_input = [context, query] 
    
    model_request = { 
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": "AdapterHub/bert-base-uncased-pf-boolq"
    }
    output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="sequence-classification", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{output}")

    # Prepare prediction
    query_output = []
    answers = ["No", "Yes"]
    predictions_scores = output["model_outputs"]["logits"][0]
    for prediction_score, answer in zip(predictions_scores, answers):
        prediction = {
            "prediction_score": prediction_score,
            "prediction_output": {
                "output": answer,
                "output_score": prediction_score
            },
            "prediction_documents": [{"document": context,}] 
        }
        query_output.append(prediction)

    return QueryOutput(predictions=query_output)
