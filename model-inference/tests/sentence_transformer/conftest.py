import os

import pytest
from pre_test_setup_for_docker_caching import (
    TRANSFORMERS_TESTING_CACHE,  # SENTENCE_MODEL,
)


SENTENCE_MODEL = os.getenv("TEST_MODEL_PATH", "./model4test")
from model_inference.app.models.request import PredictionRequest
from model_inference.main import auth, get_app
from model_inference.tasks.config.model_config import ModelConfig, model_config, set_test_config
from model_inference.tasks.inference.sentencetransformer import SentenceTransformer


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app


@pytest.fixture(scope="class")
def test_sentence_transformer():
    set_test_config(
        model_name=SENTENCE_MODEL,
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="sentence-transformer",
    )

    return SentenceTransformer()


@pytest.fixture()
def prediction_request():
    request = PredictionRequest.parse_obj(
        {
            "input": ["test"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": "",
        }
    )
    return request
