import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and a set of answer candidates, predicts the most likely answer."""

    # commonsense-qa does not take a context, but the skill-manager put the first
    # answer choice into the context field, therefore adding it back to choices
    choices = [request.skill_args["context"]] + request.skill_args["choices"]
    prepared_input = [[request.query, c] for c in choices]
    
    explain_kwargs = request.skill_args.get("explain_kwargs", {})
    
    model_request = {
        "input": prepared_input,
        "explain_kwargs": explain_kwargs,
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
        answers=choices, model_api_output=model_api_output
    )
