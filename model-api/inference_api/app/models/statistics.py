from typing import Optional

from pydantic import BaseModel


class ModelStatistics(BaseModel):
    """
    Model for displaying the statistics about the deployed model.
    """
    model_type: str  # the model type e.g. transformer, onnx, adapter
    model_name: str  # the model e.g. bert-base-cased
    batch_size: int  # the batch size for the model
    max_input: int
    model_class: str  # for transformers which model class this is e.g. base
    disable_gpu: bool
    return_plaintext_arrays: bool
    preloaded_adapters: bool
    transformers_cache: Optional[str] = ".cache"
    model_path: Optional[str] = ""
    decoder_path: Optional[str] = ""


class UpdateModel(BaseModel):
    """
    Model for updating the deployed model with new configuration.
    """
    disable_gpu: Optional[bool] = None
    batch_size: Optional[int] = None
    max_input: Optional[int] = None
    return_plaintext_arrays: Optional[bool] = None
