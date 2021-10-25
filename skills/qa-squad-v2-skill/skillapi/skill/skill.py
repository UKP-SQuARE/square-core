import base64
import logging
import uuid
from io import BytesIO
from typing import Iterable

import json

import requests
import numpy as np

from skillapi.core.config import DATA_API_URL, MODEL_API_URL, MODEL_API_KEY
from skillapi.models.prediction import QueryOutput
from skillapi.models.request import QueryRequest

logger = logging.getLogger(__name__)

def decode_model_api_response(model_api_response):
    """
    Decode (if necessary) the model output of the Model API response and make it into
    np arrays.
    :param model_api_response: The response from the API
    :return: model_api_response with 'model_outputs' decoded and parsed to numpy
    """
    # Decode byte base64 string back to numpy array
    def _decode(arr_string_b64):
        arr_binary_b64 = arr_string_b64.encode()
        arr_binary = base64.decodebytes(arr_binary_b64)
        arr = np.load(BytesIO(arr_binary))
        return arr
    # Recursively go through a value and decodeleaves (=str) or iterate over values and decode them
    def dec_or_iterate(val):
        if isinstance(val, str):
            return _decode(val)
        elif isinstance(val, Iterable):
            return [dec_or_iterate(v) for v in val]
        else:
            raise ValueError(f"Encountered unexpected value {type(val)} while trying to decode the model output of the model API. "
                             f"Expected str or iterable.")
    if model_api_response["model_output_is_encoded"]:
        model_api_response["model_outputs"] = {key: dec_or_iterate(arr) for key, arr in model_api_response["model_outputs"].items()}
    else:
        model_api_response["model_outputs"] = {key: np.array(arr) for key, arr in model_api_response["model_outputs"].items()}
    return model_api_response


async def call_model_api(url, model_request):
    """
    Call the Model API with the given complete URL (http://<host>:<port>/api/<model_name>/<endpoint>) and request.
    The 'model_outputs' will be decoded if necessary and made into np arrays before returning.
    :param url: The complete URL to send the request to
    :param model_request: the request to use for the call
    :return: The response from the Model API. If the request was not succesfull, an exception is raised.
    """
    response = requests.post(url, json=model_request, headers={"Authorization": MODEL_API_KEY})
    if response.status_code == 200:
        return decode_model_api_response(response.json())
    else:
        raise RuntimeError(f"Request to model API at URL {url} with request {model_request} "
                           f"failed with code {response.status_code} and message {response.text}")


async def call_data_api(url, data_request):
    """
    Call the Data API with the given complete URL (http://<host>:<port>/datastore/<datastore_name>/indexs/<index_name>/search) and request.
    The 'model_outputs' will be decoded if necessary and made into np arrays before returning.
    :param url: The complete URL to send the request to
    :param model_request: the request to use for the call
    :return: The response from the Data API. If the request was not succesfull, an exception is raised.
    """
    response = requests.get(url, params=data_request)
    if response.status_code == 200:
        return response.json()["root"]["children"]
    else:
        raise RuntimeError(f"Request to data API at URL {url} with request {data_request} "
                           f"failed with code {response.status_code} and message {response.text}")


# Example prediction function for question answering.
# We first retrieve documents with die Data API
# Then we use the Model API to perform span extraction
async def predict(request: QueryRequest) -> QueryOutput:
    """
    Process a given query and create the predictions for it.
    :param request: The user query
    :return: The prediction produced by the skill
    """
    context = request.skill_args["context"]
    # Call Model API
    prepared_input = [[request.query, context]]  # Change as needed
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 10},
        "adapter_name": "qa/squad2@ukp"
    }

    # Format depends on your task/ endpoint - check out the Model API
    # or square-core/square-model-inference-api/inference_server/square_model_inference/models/prediction.py
    url = f"{MODEL_API_URL}/bert-base-uncased/question-answering"
    output = await call_model_api(url, model_request)
    logger.info(output)
    # Prepare prediction
    query_output = []
    for ans in output["answers"][0]:
        if not ans["answer"]:
            continue

        prediction_score = ans["score"]

        prediction_output = {
            "output": ans["answer"],  # Set based on output
            "output_score": prediction_score
        }

        prediction_documents = [{
            "index": "",
            "document_id": "",
            "document": context,
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
                "index": "",
                "document_id": "",
                "document": context,
                "span": [0, 0],
                "source": "",
                "url": ""
            }]
        }
        query_output.append(prediction)

    query_output = sorted(query_output, key=lambda item: item["prediction_score"], reverse=True)

    return QueryOutput(predictions=query_output)
