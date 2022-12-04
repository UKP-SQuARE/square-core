import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:

    query = request.query
    # HACK: the UI currently does not support choices, therefore the first choice will
    # be processed insde the context.
    choices = request.skill_args["choices"]
    model_kwargs = request.skill_args.get("model_kwargs", {})
    model_kwargs["output_lm_subgraph"] = model_kwargs.get("output_lm_subgraph", True)
    model_kwargs["output_attn_subgraph"] = model_kwargs.get(
        "output_attn_subgraph", True
    )

    explain_kwargs = request.explain_kwargs or {}
    attack_kwargs = request.attack_kwargs or {}

    prepared_input = [[query, choice] for choice in choices]

    # Call Model API
    model_request = {
        "input": prepared_input,
        "model_kwargs": model_kwargs,
        "explain_kwargs": explain_kwargs,
        "attack_kwargs": attack_kwargs,
    }
    logger.debug("Request for model api:{}".format(model_request))

    model_response = await square_model_client(
        model_name="qagnn",
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info("Model response: {}".format(model_response))

    return QueryOutput.from_sequence_classification_with_graph(
        questions=query, answers=choices, model_api_output=model_response
    )
