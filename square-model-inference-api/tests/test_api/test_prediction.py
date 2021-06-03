def test_prediction(test_client) -> None:
    response = test_client.post(
        "/api/v1/question",
        json={"context": "two plus two equal four", "question": "What is four?"},
        headers={"token": "example_key"},
    )
    assert response.status_code == 200
    assert "score" in response.json()


def test_prediction_nopayload(test_client) -> None:
    response = test_client.post(
        "/api/v1/question", json={}, headers={"token": "example_key"}
    )
    """
    ## if nopayload, default Hitchhiker's Guide to the Galaxy example is sent
    # context:"42 is the answer to life, the universe and everything."
    # question:"What is the answer to life?"
    # if no default, assert response.status_code == 422
    """

    data = response.json()
    assert data["answer"] == "42"
