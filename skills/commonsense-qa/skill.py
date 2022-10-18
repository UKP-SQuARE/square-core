import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and a set of answer candidates, predicts the most likely answer."""

    query = request.query
    choices = request.skill_args["choices"]
    prepared_input = [[query, c] for c in choices]

    explain_kwargs = request.explain_kwargs or {}
    attack_kwargs = request.attack_kwargs or {}

    model_request = {
        "input": prepared_input,
        "explain_kwargs": explain_kwargs,
        "attack_kwargs": attack_kwargs,
    }
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_sequence_classification(
        questions=query, answers=choices, model_api_output=model_api_output
    )
