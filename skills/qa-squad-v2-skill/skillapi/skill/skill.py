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
    context = request.skill_args["context"]

    prepared_input = [[request.query, context]]  # Change as needed
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 10},
        "adapter_name": "qa/squad2@ukp"
    }

    model_api_output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="question-answering", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_question_answering(
        model_api_output=model_api_output,
        context=context
    )

