from starlette.testclient import TestClient

def test_api_correct_auth(test_app, test_key, test_header) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        "/auth",
        headers={test_header: test_key}
    )
    assert response.status_code == 200
    assert response.json()["authenticated"] == True


def test_api_no_header(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        "/auth"
    )
    assert response.status_code == 400

def test_api_wrong_header(test_app, test_key, test_header) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        "/auth",
        headers={test_header+"wrong": test_key}
    )
    assert response.status_code == 400

def test_api_wrong_key(test_app, test_key, test_header) -> None:
    test_client = TestClient(test_app)
    response = test_client.get(
        "/auth",
        headers={test_header: test_key+"wrong"}
    )
    assert response.status_code == 401