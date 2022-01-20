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
    query = request.query
    context = request.skill_args.get("context")
    answers = request.skill_args["answers"]

    if request.skill_args.get("skill_type") == "categorical":
        prepared_input = [[context, query]]
    else:
        if context is not None:
            prepared_input = [[context, query + " " + answer] for answer in answers]
        else:
            prepared_input = [[query, answer] for answer in answers]

    # Call Model API
    model_request = {
        "input": prepared_input,
        "adapter_name": request.skill_args["adapter"],
    }

    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_sequence_classification(
        answers=answers, model_api_output=model_api_output, context=context
    )
