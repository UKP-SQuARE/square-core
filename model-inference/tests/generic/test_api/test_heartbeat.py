from starlette.testclient import TestClient


def test_heartbeat(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get("/api/health/heartbeat")
    assert response.status_code == 200
    assert response.json() == {"is_alive": True}

def test_default_route(test_app) -> None:
    test_client = TestClient(test_app)
    response = test_client.get("/")
    assert response.status_code == 404
