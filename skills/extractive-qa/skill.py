import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    query = request.query
    context = request.skill_args["context"]
    explain_kwargs = request.explain_kwargs or {}
    prepared_input = [[query, context]]
    model_request = {
        "input": prepared_input,
        "task_kwargs": {"topk": request.skill_args.get("topk", 5)},
        "explain_kwargs": explain_kwargs,
    }
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]

    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_question_answering(
        questions=query, model_api_output=model_api_output, context=context
    )
