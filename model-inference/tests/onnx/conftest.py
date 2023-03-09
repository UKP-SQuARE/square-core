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
    model_name = "UKP-SQuARE/bert-base-uncased-pf-squad-onnx"
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
    model_name = "UKP-SQuARE/roberta-base-pf-squad-onnx"
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
    model_name = "UKP-SQuARE/roberta-base-pf-boolq-onnx"
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
def test_onnx_sequence_classification():
    model_name = "UKP-SQuARE/roberta-base-pf-boolq-onnx"
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
def test_onnx_token_classification():
    model_name = "optimum/bert-base-NER"
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
def test_onnx_embedding():
    model_name = "UKP-SQuARE/bert-base-cased-onnx"
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
def test_onnx_generation():
    model_name = "optimum/t5-small"
    set_test_config(
        model_name=model_name,
        is_encoder_decoder=True,
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        model_type="onnx",
    )
    return Onnx()
