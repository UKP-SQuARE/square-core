from unittest.mock import patch

from starlette.testclient import TestClient
from celery.result import AsyncResult

from tasks.models.request import Task


identifier = "test_config"


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_sequence_classification(test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        f"/api/{identifier}/sequence-classification",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    print("check task", Task.sequence_classification)
    assert test_task.called
    assert test_task.call_args[1] == {"queue": identifier}
    assert test_task.call_args[0][0][1] == Task.sequence_classification
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_sequence_classification_malformed_input(test_task, test_app) -> None:
    test_client = TestClient(test_app, raise_server_exceptions=False)
    response = test_client.post(
        f"/api/{identifier}/sequence-classification", json={
            # "input": [
            #     "this is a test"
            # ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert not test_task.called
    assert response.status_code == 422


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_token_classification(test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        f"/api/{identifier}/token-classification",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert test_task.called
    assert test_task.call_args[1] == {"queue": identifier}
    assert test_task.call_args[0][0][1] == Task.token_classification
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_embedding(test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        f"/api/{identifier}/embedding",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert test_task.called
    assert test_task.call_args[1] == {"queue": identifier}
    assert test_task.call_args[0][0][1] == Task.embedding
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_question_answering(test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        f"/api/{identifier}/question-answering",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert test_task.called
    assert test_task.call_args[1] == {"queue": identifier}
    assert test_task.call_args[0][0][1] == Task.question_answering
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
def test_api_generation(test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        f"/api/{identifier}/generation",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert test_task.called
    assert test_task.call_args[1] == {"queue": identifier}
    assert test_task.call_args[0][0][1] == Task.generation
    assert response.status_code == 200


def test_api_statistics(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        f"/api/{identifier}/stats",
    )
    assert response.json()["model_type"] == "adapter"
    assert response.json()["model_name"] == "bert-base-uncased"
    assert response.json()["max_input"] == 512
    assert response.status_code == 200
