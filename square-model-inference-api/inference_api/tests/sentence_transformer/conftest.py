import pytest
import os
from pre_test_setup_for_docker_caching import (
    # SENTENCE_MODEL,
    TRANSFORMERS_TESTING_CACHE,
)
SENTENCE_MODEL = os.getenv("TEST_MODEL_PATH","./model4test")
from main import get_app, auth

from tasks.inference.sentencetransformer import SentenceTransformer

from tasks.config.model_config import ModelConfig, set_test_config, model_config
from app.models.request import PredictionRequest




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
    request = PredictionRequest.parse_obj({
        "input": ["test"],
        "is_preprocessed": False,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {},
        "adapter_name": ""
    })
    return request
