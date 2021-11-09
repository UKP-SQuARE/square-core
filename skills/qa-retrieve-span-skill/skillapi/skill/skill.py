import logging
import uuid

from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import ModelAPI, DataAPI

logger = logging.getLogger(__name__)

config = SquareSkillHelpersConfig.from_dotenv()
model_api = ModelAPI(config)
data_api = DataAPI(config)

async def predict(request: QueryRequest) -> QueryOutput:
    """
    Process a given query and create the predictions for it.
    :param request: The user query
    :return: The prediction produced by the skill
    """
    # Call Data API
    data_request = {  # Fill as needed
        "query": request.query,
        "top_k": request.num_results
    }
    data = await DataAPI(datastore="wiki", index_name="dpr", data_request=data_request)
    logger.info(f"Data API output:\n{data}")

    # Call Model API
    prepared_input = [[request.query, d["fields"]["text"]] for d in data]  # Change as needed
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 1},
        "adapter_name": "qa/squad2@ukp"
    }

    output = await model_api(
        model_name="bert-base-uncased", 
        pipline="question-answering", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{output}")

    # Prepare prediction
    query_output = []
    index_name = "wiki/dpr"
    for d, ans in zip(data, output["answers"]):
        ans = ans[0]
        if not ans["answer"]:
            continue

        prediction_score = ans["score"]

        prediction_output = {
            "output": ans["answer"],  # Set based on output
            "output_score": prediction_score
        }

        prediction_documents = [{
            "index": index_name,
            "document_id": d["fields"]["documentid"],
            "document": d["fields"]["text"],
            "span": [ans["start"], ans["end"]],
            "source": "",
            "url": ""
        }]  # Change as needed

        # Return
        prediction_id = str(uuid.uuid4())
        prediction = {
            "prediction_id": prediction_id,
            "prediction_score": prediction_score,
            "prediction_output": prediction_output,
            "prediction_documents": prediction_documents
        }
        query_output.append(prediction)

    # Answer for no answer
    if len(query_output) == 0:
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_score": max(ans[0]["score"] for ans in output["answers"]),
            "prediction_output": {
                "output": "No answer found in the searched documents",
                "output_score": max(ans[0]["score"] for ans in output["answers"])
            },
            "prediction_documents": [{
                "index": index_name,
                "document_id": d["fields"]["documentid"],
                "document": d["fields"]["text"],
                "span": [0, 0],
                "source": "",
                "url": ""
            } for d in data]
        }
        query_output.append(prediction)

    query_output = sorted(query_output, key=lambda item: item["prediction_score"], reverse=True)

    return QueryOutput(predictions=query_output)
