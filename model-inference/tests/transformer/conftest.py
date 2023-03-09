import os

import pytest
from pre_test_setup_for_docker_caching import (
    TRANSFORMERS_TESTING_CACHE,  # TRANSFORMER_MODEL,
)


TRANSFORMER_MODEL = os.getenv("TEST_MODEL_PATH", "./model4test")
import torch
from model_inference.app.models.request import PredictionRequest
from model_inference.main import auth, get_app
from model_inference.tasks.config.model_config import (
    ModelConfig,
    model_config,
    set_test_config,
)
from model_inference.tasks.inference.adaptertransformer import AdapterTransformer
from model_inference.tasks.inference.transformer import Transformer


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app


# We only load bert-base-uncased, so we fix the random seed to always get the same randomly generated heads on top
@pytest.fixture(scope="class")
def test_transformer_sequence_classification():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="sequence_classification",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformer",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_embedding():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="base",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformers",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_token_classification():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="token_classification",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformers",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_question_answering():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="question_answering",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformers",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_explainability():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="question_answering",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformers",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_generation():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="generation",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="transformers",
    )
    return Transformer()


@pytest.fixture(scope="class")
def test_adapter():
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        cache=TRANSFORMERS_TESTING_CACHE,
        preloaded_adapters=False,
        model_type="adapter",
    )
    return AdapterTransformer()


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
