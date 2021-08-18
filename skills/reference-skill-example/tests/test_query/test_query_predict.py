import pytest

from skillapi.models.request import QueryRequest
from skillapi.skill.skill import decode_model_api_response, call_model_api, call_data_api, predict
import numpy as np

class Response:
    def __init__(self, status_code, json={}, text=""):
        self._json = json
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._json


def mock_request(response_json, status_code=200, error_text=""):
    def f(url, json={}, params={}, headers={}):
        return Response(status_code, json=response_json, text=error_text)
    return f


def test_decode_model_api_response_encoded(model_api_question_answering_response):
    model_api_question_answering_response = decode_model_api_response(model_api_question_answering_response)
    assert isinstance(model_api_question_answering_response["model_outputs"]["start_logits"], np.ndarray)


def test_decode_model_api_response_list(model_api_question_answering_response):
    model_api_question_answering_response["model_output_is_encoded"] = False
    model_api_question_answering_response["model_outputs"]["start_logits"] = [[1, 0.5, 4.2]]
    model_api_question_answering_response = decode_model_api_response(model_api_question_answering_response)
    assert isinstance(model_api_question_answering_response["model_outputs"]["start_logits"], np.ndarray)


@pytest.mark.asyncio
async def test_model_api_call(mocker, model_api_question_answering_response):
    mocker.patch("skillapi.skill.skill.requests.post", mock_request(model_api_question_answering_response, 200))
    res = await call_model_api("url", {})


@pytest.mark.asyncio
async def test_model_api_call_error(mocker):
    mocker.patch("skillapi.skill.skill.requests.post", mock_request({}, 500, "Error"))
    with pytest.raises(RuntimeError):
        res = await call_model_api("url", {})


@pytest.mark.asyncio
async def test_data_api_call(mocker, data_api_response):
    mocker.patch("skillapi.skill.skill.requests.get", mock_request(data_api_response, 200))
    res = await call_data_api("url", {})


@pytest.mark.asyncio
async def test_data_api_call_error(mocker):
    mocker.patch("skillapi.skill.skill.requests.get", mock_request({}, 500, "Error"))
    with pytest.raises(RuntimeError):
        res = await call_data_api("url", {})


@pytest.mark.asyncio
async def test_predict(mocker, model_api_question_answering_response, data_api_response) -> None:
    mocker.patch("skillapi.skill.skill.requests.post", mock_request(model_api_question_answering_response, 200))
    mocker.patch("skillapi.skill.skill.requests.get", mock_request(data_api_response, 200))
    res = await predict(QueryRequest(**{"query": "The query", "num_results": 1, "skill_args": {}, "user_id": "1234"}))
    pass
