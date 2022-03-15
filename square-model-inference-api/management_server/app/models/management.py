from typing import Optional
from pydantic import Field, BaseModel

# Response and request models for the management server


class GetModelsResult(BaseModel):
    """list the models deployed on the platform"""

    identifier: str = Field(description="The identifier to reach the model")
    model_type: str = Field(description="transformer, adapter, onnx, or sentence-transformer")
    model_name: str = Field(description="name of the model")
    disable_gpu: bool = Field(description="whether to use gpu for inference")
    batch_size: int = Field(description="input batch size")
    max_input: int = Field(description="max input length")
    model_class: str = Field(description="See square_model_inference.inference.transformer.CLASS_MAPPING "
                                         "for valid names and corresponding class")
    return_plaintext_arrays: bool = Field(description="whether to encode outputs")


class GetModelsHealth(BaseModel):
    identifier: str
    is_alive: bool


class DeployRequest(BaseModel):
    """Request model for model deployment"""
    identifier: str = Field("", description="the name given by the user through which the model can be accessed "
                                            "after deployment")
    model_name: str = Field("", description="the name of model on HF, AdapterHub or sentence-transformers platform")
    model_path: Optional[str] = Field(None, description="model path for the ONNX models")
    decoder_path: Optional[str] = Field(None, description="path of the decoder ONNX model")
    model_type: str = Field("", description="transformer, adapter, onnx, or sentence-transformer")
    disable_gpu: Optional[bool] = Field(True, description="whether to use gpu for inference")
    batch_size: int = Field("", description="input batch size")
    max_input: int = Field("", description="max input length")
    transformers_cache: Optional[str] = Field("../.cache", description="path to cache models")
    model_class: str = Field("", description="See square_model_inference.inference.transformer.CLASS_MAPPING "
                                             "for valid names and corresponding class")
    return_plaintext_arrays: Optional[bool] = Field(False, description="whether to encode outputs")
    preloaded_adapters: Optional[bool] = Field(True, description="whether to preload adapters")


class TaskGenericModel(BaseModel):
    """ Celery generic task representation """
    message: str = Field(..., description="Error or success message")
    task_id: str = Field(..., description="id of the task being processed by celery")


class TaskResultModel(BaseModel):
    """Celery task response """
    task_id: str = Field(..., description="id of the task being processed by celery")
    status: str = Field(..., description="status of the celery task being processed")
    result: dict = Field(..., description="the response from the requested endpoint")


class UpdateModel(BaseModel):
    disable_gpu: Optional[bool] = None
    batch_size: Optional[int] = None
    max_input: Optional[int] = None
    return_plaintext_arrays: Optional[bool] = None
