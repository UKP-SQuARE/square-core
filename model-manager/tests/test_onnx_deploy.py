import pytest
from model_manager.app.models.onnx_export import onnx_export, auto_onnx_config
from transformers.models.bart import BartOnnxConfig

@pytest.mark.parametrize(
    'model_name', (["UKP-SQuARE/this-model-does-not-exist"])
)
def test_model_does_not_exist(model_name) -> None:
    with pytest.raises(EnvironmentError):
        onnx_export(model_name, "", "", "", "")


@pytest.mark.parametrize(
    'model_name', (["facebook/bart-base"])
)
def test__auto_onnx_config(model_name) -> None:
    onnx_config = auto_onnx_config(model_name, "default")
    assert type(onnx_config) is BartOnnxConfig


@pytest.mark.parametrize(
    'model_name', (["SpanBERT/spanbert-large-cased"])
)
def test_no_auto_onnx_config(model_name) -> None:
    with pytest.raises(ValueError):
        auto_onnx_config(model_name, "default")


@pytest.mark.parametrize(
    'model_params',
    (
    [
        "UKP-SQuARE/distilbert-base-uncased-onnx",
        {
            "model_name": "distilbert-base-uncased",
            "onnx_use_quantized": True,
            "model_class": "default",
            "adapter_id": "",
            "custom_onnx_config": "",
        },
    ],
    [
        "UKP-SQuARE/spanbert-base-cased-onnx",
        {
            "model_name": "SpanBERT/spanbert-base-cased",
            "onnx_use_quantized": True,
            "model_class": "default",
            "adapter_id": "",
            "custom_onnx_config": '{"input_ids": {"0": "batch", "1": "sequence"}, "attention_mask": {"0": "batch", "1": "sequence"}, "token_type_ids": {"0": "batch", "1": "sequence"}}',
        },
    ],
    [
        "UKP-SQuARE/bert-base-uncased-pf-hotpotqa-onnx",
        {
            "model_name": "bert-base-uncased",
            "onnx_use_quantized": True,
            "model_class": "question-answering",
            "adapter_id": "hotpotqa",
            "custom_onnx_config": "",
        },
    ],
    ),
    indirect=True
)
def test_onnx_export(hf_token, model_params) -> None:
    model_name = onnx_export(model_params[1]["model_name"] 
                    ,model_params[1]["model_class"] 
                    ,hf_token
                    ,model_params[1]["adapter_id"] 
                    ,model_params[1]["custom_onnx_config"] 
                    ,model_params[1]["onnx_use_quantized"] 
                    )

    assert model_name == model_params[0]