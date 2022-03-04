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
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    query = request.query
    context = request.skill_args.get("context")

    if context:
        query_context_seperator = request.skill_args.get("query_context_seperator", " ")
        prepared_input = [query + query_context_seperator + context]
    else:
        prepared_input = [query]
    model_request = {
        "input": prepared_input,
        "model_kwargs": {
            "output_scores": True,
            **request.skill_args.get("model_kwargs", {}),
        },
        "adapter_name": request.skill_args["adapter"],
    }

    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="generation",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_generation(
        model_api_output=model_api_output, context=context
    )
