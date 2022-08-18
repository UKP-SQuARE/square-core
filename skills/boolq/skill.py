import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Predicts yes/no for a boolean question with context"""
    query = request.query
    context = request.skill_args["context"]
    explain_kwargs = request.explain_kwargs or {}
    attack_kwargs = request.attack_kwargs or {}

    prepared_input = [[context, query]]

    model_request = {
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": request.skill_args["adapter"],
        "explain_kwargs": explain_kwargs,
        "attack_kwargs": attack_kwargs,
    }
    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_sequence_classification(
        questions=query,
        answers=["No", "Yes"],
        model_api_output=model_api_output,
        context=context,
    )
