from asyncio import Future

import pytest
from starlette.testclient import TestClient
from skillapi.models.prediction import QueryOutput


def test_api(mocker, test_app) -> None:
    async def predict(query):
        return {"predictions": [{
        "prediction_id": "id",
        "prediction_output": {
            "output": "output",
            "output_score": 1.0
        },
        "prediction_documents": [],
        "prediction_score": 1.0
    }]}
    mocker.patch("skillapi.api.routes.query.predict",
                 predict
                 )
    test_client = TestClient(test_app)

    response = test_client.post(
        "/query",
        json={
            "query": "What is is the airspeed velocity of an unladen swallow?",
            "skill_args": {},
            "num_results": 1
        }
    )
    assert response.status_code == 200

