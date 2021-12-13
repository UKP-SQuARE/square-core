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

    answers = request.skill_args.get("answers")
    if answers is None:
        answers = request.skill_args["context"].split("\n")

    prepared_input = [[request.query, c] for c in answers] 
    model_request = { 
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": "AdapterHub/bert-base-uncased-pf-commonsense_qa"
    }
    model_api_output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="sequence-classification", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_sequence_classification(
        answers=answers, model_api_output=model_api_output
    )
