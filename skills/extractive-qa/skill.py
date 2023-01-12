import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    query = request.query
    context = request.skill_args["context"]
    explain_kwargs = request.explain_kwargs or {}
    attack_kwargs = request.attack_kwargs or {}
    prepared_input = [[query, context]]
    model_request = {
        "input": prepared_input,
        "task_kwargs": {
            "topk": request.skill_args.get("topk", 5),
            "show_null_answers": request.skill_args.get("show_null_answers", True),
        },
        "explain_kwargs": explain_kwargs,
        "attack_kwargs": attack_kwargs,
    }
    if request.skill_args.get("adapter"):
        if request.skill_args.get("average_adapters"):
            model_request["adapter_name"] = request.skill_args["adapter"]
            model_request["model_kwargs"]['average_adapters'] = True
        else:
            model_request["adapter_name"] = request.skill_args["adapter"]

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_question_answering(
        questions=query, model_api_output=model_response, context=context
    )
