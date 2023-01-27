import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    query = request.query
    context = request.skill_args.get("context", "")

    if context:
        query_context_seperator = request.skill_args.get("query_context_seperator", " ")
        prepared_input = [query + query_context_seperator + context]
    else:
        prepared_input = [query]

    model_request_kwargs = extract_model_kwargs_from_request(request)
    output_scores = request.skill_args.get("model_kwargs", {}).get(
        "output_scores", True
    )
    model_request_kwargs["model_kwargs"]["output_scores"] = output_scores

    model_request = {"input": prepared_input, **model_request_kwargs}
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="generation",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_generation(
        questions=query, model_api_output=model_response, context=context
    )
