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
            "query": "do iran and afghanistan speak the same language",
            "skill_args": {
                "context": "Persian language -- Persian (/ˈpɜːrʒən, -ʃən/), also known by its endonym Farsi (فارسی fārsi (fɒːɾˈsiː) ( listen)), is one of the Western Iranian languages within the Indo-Iranian branch of the Indo-European language family. It is primarily spoken in Iran, Afghanistan (officially known as Dari since 1958), and Tajikistan (officially known as Tajiki since the Soviet era), and some other regions which historically were Persianate societies and considered part of Greater Iran. It is written in the Persian alphabet, a modified variant of the Arabic script, which itself evolved from the Aramaic alphabet."
            },
            "num_results": 1,
            "user_id": "1234"
        }
    )
    assert response.status_code == 200

