from starlette.testclient import TestClient


def test_api_sequence_classification(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/sequence-classification",
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
    assert response.status_code == 200


def test_api_sequence_classification_malformed_input(test_app) -> None:
    test_client = TestClient(test_app, raise_server_exceptions=False)
    response = test_client.post(
        "/api/sequence-classification", json={
            # "input": [
            #     "this is a test"
            # ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "task_kwargs": {},
            "adapter_name": ""
        }
    )
    assert response.status_code == 422


def test_api_token_classification(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/token-classification",
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
    assert response.status_code == 200

def test_api_embedding(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/embedding",
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
    assert response.status_code == 200


def test_api_question_answering(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/question-answering",
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
    assert response.status_code == 200


def test_api_generation(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.post(
        "/api/generation",
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
    assert response.status_code == 200