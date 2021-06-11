from starlette.testclient import TestClient


def test_prediction(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/predict",
        json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert response.status_code == 200


def test_prediction_wrong_request(test_app) -> None:
    test_client = TestClient(test_app, raise_server_exceptions=False)
    response = test_client.post(
        "/api/predict", json={
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            # required
            #"model_kwargs": {},
            #"task": "embedding",
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert response.status_code == 422
