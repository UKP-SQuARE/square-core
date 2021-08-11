import base64
import uuid
from io import BytesIO

import requests
import numpy as np

from skillapi.core.config import DATA_API_URL, MODEL_API_URL, MODEL_API_KEY
from skillapi.models.prediction import QueryOutput
from skillapi.models.request import QueryRequest


def decode_model_api_response(model_api_response):
    def _decode(arr_string_b64):
        arr_binary_b64 = arr_string_b64.encode()
        arr_binary = base64.decodebytes(arr_binary_b64)
        arr = np.load(BytesIO(arr_binary))
    if model_api_response["model_output_is_encoded"]:

    else:
        return model_api_response


async def call_model_api(url, model_request):
    response = requests.post(url, json=model_request, headers={"Authorization": MODEL_API_KEY})
    if response.status_code == 200:
        return decode_model_api_response(response.json())
    else:
        raise RuntimeError(f"Request to model API at URL {url} with request {model_request} "
                           f"failed with code {response.status_code} and message {response.text}")

async def call_data_api(url, data_request):
    response = requests.post(url, json=data_request)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Request to data API at URL {url} with request {data_request} "
                           f"failed with code {response.status_code} and message {response.text}")


async def predict(request: QueryRequest) -> QueryOutput:
    data_request = {...} # Create as needed
    data = await call_data_api(DATA_API_URL, data_request)
    processed_data = [d for d in data] # Change as needed
    model_request = { # Create as needed
        "input": processed_data,
        ...
    }
    output = await call_model_api(MODEL_API_URL, data_request)

    prediction_score = 0.1 # Set based on output

    prediction_output = {
        "output": "This is the answer", # Set based on output
        "output_score": prediction_score
    }

    prediction_documents = [{""} for d in data] # Change as needed

    prediction_id = str(uuid.uuid4())
    query_output = {
        "prediction_id": prediction_id,
        "prediction_score": prediction_score,
        "prediction_output": prediction_output,
        "prediction_documents": prediction_documents
    }
    return QueryOutput(**query_output)