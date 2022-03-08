import logging
import uuid

from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import DataAPI, ModelAPI

logger = logging.getLogger(__name__)

config = SquareSkillHelpersConfig.from_dotenv()
model_api = ModelAPI(config)
data_api = DataAPI(config)


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, performs open-domain, extractive QA. First, background
    knowledge is retrieved using a specified index and retrieval method. Next, the top k
    documents are used for span extraction. Finally, the extracted answers are returned.
    """

    query = request.query

    data = await data_api(
        datastore_name=request.skill_args["datastore"],
        index_name=request.skill_args.get("index", ""),
        query=query,
    )
    logger.info(f"Data API output:\n{data}")
    context = [d["document"]["text"] for d in data]
    context_score = [d["score"] for d in data]

    prepared_input = [[query, c] for c in context]
    model_request = {
        "input": prepared_input,
        "task_kwargs": {"topk": request.skill_args.get("topk", 5)},
        "adapter_name": request.skill_args["adapter"],
    }
    model_api_output = await model_api(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_question_answering(
        model_api_output=model_api_output, context=context, context_score=context_score
    )
