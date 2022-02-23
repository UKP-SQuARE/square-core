import logging
import uuid

from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, a set of answers and optional context, performs multiple-choice 
    QA. This skill is a general skill, it can be used with any adapter for 
    multiple-choice question answering. The adapter to use can be specified in the 
    `skill_args` or via the `default_skill_args` in the skill-manager.
    """
    query = request.query
    context = request.skill_args.get("context")
    answers = request.skill_args["answers"]

    # BUG: for categorical skills, answers do not need to be appended
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
