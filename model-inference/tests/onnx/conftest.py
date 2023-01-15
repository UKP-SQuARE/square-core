import os

import pytest
from model_inference.app.models.request import PredictionRequest
from model_inference.main import auth, get_app
from model_inference.tasks.config.model_config import set_test_config
from model_inference.tasks.inference.onnx import Onnx


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.dependency_overrides[auth] = lambda: True
    return app

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


@pytest.fixture(scope="class")
def test_onnx_question_answering():
    model_name = "bert-base-uncased-pf-squad-onnx"
    set_test_config(
            model_name=model_name,
            onnx_use_quantized=False,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            model_type="onnx",
        )
    return Onnx()

@pytest.fixture(scope="class")
def test_onnx_quantized_question_answering():
    model_name = "roberta-base-pf-squad-onnx"
    set_test_config(
            model_name=model_name,
            onnx_use_quantized=True,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            model_type="onnx",
        )
    return Onnx()


@pytest.fixture(scope="class")
def test_onnx_categorical():
    model_name = "roberta-base-pf-boolq-onnx"
    set_test_config(
            model_name=model_name,
            onnx_use_quantized=False,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            model_type="onnx",
        )
    return Onnx()

# Non-QA onnx models are not yet exported to Huggingface and therefor tested with local models
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