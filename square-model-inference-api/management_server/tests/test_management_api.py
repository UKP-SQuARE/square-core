from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient
from celery.result import AsyncResult

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

@patch('mongo_access.MongoClass.get_models_db', return_value=[{"IDENTIFIER": "test_identifier",
                "MODEL_TYPE": "adapter",
                "MODEL_NAME": "bert-base-uncased",
                "DISABLE_GPU": True,
                "BATCH_SIZE": 4,
                "MAX_INPUT_SIZE": 1024,
                "MODEL_CLASS": "base",
                "RETURN_PLAINTEXT_ARRAYS": True,}], new_callable=AsyncMock)
def test_api_deployed_models(test_mongo, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        f"/api/deployed-models",
    )
    assert response.json()[0]["identifier"] == "test_identifier"
    assert response.json()[0]["model_type"] == "adapter"
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
@patch('mongo_access.MongoClass.check_identifier_new', return_value=True, new_callable=AsyncMock)
def test_api_deploy(test_check, test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/deploy",
        json={
            "identifier": "test",
            "model_name": "bert-base-uncased",
            "model_type": "transformer",
            "disable_gpu": True,
            "batch_size": 32,
            "max_input": 1024,
            "transformers_cache": "../.cache",
            "model_class": "base",
            "return_plaintext_arrays": False,
            "preloaded_adapters": True
        }
    )
    assert test_task.called
    assert response.status_code == 200


@patch('celery.app.task.Task.delay',  return_value=AsyncResult(123))
@patch('mongo_access.MongoClass.check_identifier_new', return_value=False, new_callable=AsyncMock)
@patch('mongo_access.MongoClass.check_user_id', return_value=True, new_callable=AsyncMock)
def test_api_remove(test_check1, test_check2, test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.delete(
        "/api/remove/test_identifier",
    )
    assert test_task.called
    assert response.status_code == 200

@patch('celery.app.task.Task.delay',  return_value=AsyncResult(123))
@patch('mongo_access.MongoClass.check_identifier_new', return_value=True, new_callable=AsyncMock)
def test_api_remove_not_existing(test_check, test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.delete(
        "/api/remove/test_identifier",
    )
    assert not test_task.called
    assert response.status_code == 406