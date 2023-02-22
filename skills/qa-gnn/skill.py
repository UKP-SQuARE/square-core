import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    query = request.query
    choices = request.skill_args["choices"]
    prepared_input = [[query, choice] for choice in choices]

    model_request_kwargs = extract_model_kwargs_from_request(request)

    ols_default = model_request_kwargs["model_kwargs"].get("output_lm_subgraph", True)
    model_request_kwargs["model_kwargs"]["output_lm_subgraph"] = ols_default

    oas_default = model_request_kwargs["model_kwargs"].get("output_attn_subgraph", True)
    model_request_kwargs["model_kwargs"]["output_attn_subgraph"] = oas_default

    model_request = {"input": prepared_input, **model_request_kwargs}
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
