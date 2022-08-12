import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:

    query = request.query
    # HACK: the UI currently does not support choices, therefore the first choice will
    # be processed insde the context.
    choices = [request.skill_args["context"]] + request.skill_args["choices"]
    model_kwargs = request.skill_args.get("model_kwargs", {})
    model_kwargs["output_lm_subgraph"] = model_kwargs.get("output_lm_subgraph", True)
    model_kwargs["output_attn_subgraph"] = model_kwargs.get(
        "output_attn_subgraph", True
    )

    explain_kwargs = request.explain_kwargs or {}
    adversarial_kwargs = request.adversarial_kwargs or {}

    prepared_input = [[query, choice] for choice in choices]

    # Call Model API
    model_request = {
        "input": prepared_input,
        "model_kwargs": model_kwargs,
        "explain_kwargs": explain_kwargs,
        "adversarial_kwargs": adversarial_kwargs,
    }
    logger.debug("Request for model api:{}".format(model_request))

    model_api_output = await model_api(
        model_name="qagnn",
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info("Model API output: {}".format(model_api_output))

    return QueryOutput.from_sequence_classification_with_graph(
        questions=query, answers=choices, model_api_output=model_api_output
    )
