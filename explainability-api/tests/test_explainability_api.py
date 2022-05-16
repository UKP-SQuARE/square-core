from pathlib import Path
from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient
from celery.result import AsyncResult


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def test_heartbeat(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get("/api/health/heartbeat")
    assert response.status_code == 200
    assert response.json() == {"is_alive": True}


def test_default_route(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get("/")
    assert response.status_code == 404


@patch(
    'app.db.mongo_operations.Database.add_tests_to_db', return_value=True
    , new_callable=AsyncMock
)
def test_api_add_tests(test_mongo, test_app) -> None:
    test_client = TestClient(test_app)
    _test_upload_file = Path('checklists/', 'boolean_model_tests.json')
    files = [('file', ('boolean_model_tests.json', open(_test_upload_file, 'rb'),
                       'application/json'))]
    response = test_client.put(
        f"/api/checklist/tests",
        files=files,
    )
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
@patch(
    'app.db.mongo_operations.Database.add_results_to_db', return_value=True
    , new_callable=AsyncMock
)
@patch(
    'app.api.auth.get_user_id', return_value="ukp"
    , new_callable=AsyncMock
)
def test_api_execute_checklist_single(test_check1, test_check2, test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.put(
        f"/api/checklist/execute-single",
        params={"skill_name": "CosmosQA BERT"}
    )
    assert test_task.called
    assert test_task.call_args[0][0][0]["name"] == "CosmosQA BERT"
    assert response.status_code == 200


@patch('celery.app.task.Task.apply_async',  return_value=AsyncResult(123))
@patch(
    'app.db.mongo_operations.Database.add_results_to_db', return_value=True
    , new_callable=AsyncMock
)
@patch(
    'app.db.mongo_operations.Database.get_skills_from_results_db', return_value=["61a9f68535adbbf1f2433078"]
    , new_callable=AsyncMock
)
@patch(
    'app.api.auth.get_user_id', return_value="ukp"
    , new_callable=AsyncMock
)
def test_api_execute_checklist_all(test_check1, test_check2, test_check3, test_task, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.put(
        f"/api/checklist/execute-all",
    )
    assert test_task.called
    assert response.status_code == 200


@patch(
    'app.db.mongo_operations.Database.get_results', return_value={}
    , new_callable=AsyncMock
)
def test_api_get_results(test_mongo, test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        f"/api/checklist/results",
        params={"skill_id": "61a9f68535adbbf1f2433078", "test_type": "MFT", "capability": "Vocabulary"}
    )
    assert response.status_code == 200
