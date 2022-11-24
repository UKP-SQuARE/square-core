import os

import pytest
import torch
from app.models.request import PredictionRequest
from main import auth, get_app
from pre_test_setup_for_docker_caching import ONNX_MODEL
from tasks.config.model_config import ModelConfig, model_config, set_test_config
from tasks.inference.onnx import Onnx


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app


@pytest.fixture(scope="class")
def test_onnx_sequence_classification():
    onnx_path = "./onnx_models/german-bert/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            model_type="onnx",
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_token_classification():
    onnx_path = "./onnx_models\\NER-bert\\model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            model_type="onnx",
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_embedding():
    onnx_path = "./onnx_models/bert-base-cased/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            model_type="onnx",
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_question_answering():
    onnx_path = "./onnx_models/squad2-bert/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            model_type="onnx",
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_generation():
    onnx_path = "./onnx_models/t5_encoder_decoder/t5-small-encoder.onnx"
    decoder_init_path = "./onnx_models/t5_encoder_decoder/t5-small-init-decoder.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            decoder_path=decoder_init_path,
            model_type="onnx",
        )
        return Onnx()
    else:
        return None


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
