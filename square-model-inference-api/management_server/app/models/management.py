from typing import Optional
from pydantic import Field, BaseModel

# Response and request models for the management server


class GetModelsResult(BaseModel):
    """list the deployed models on the platform"""
    identifier: str = Field(description="The identifier to reach the model")
    model_type: str = Field(description="transformer, adapter, onnx, etc.")
    model_name: str = Field(description="name of the model.")
    disable_gpu: bool = Field(description="input batch size")
    batch_size: int = Field(description="max input length")
    max_input: int = Field(description="See square_model_inference.inference.transformer.CLASS_MAPPING "
                                       "for valid names and corresponding class")
    model_class: str = Field(description="whether to use gpu for inference")
    return_plaintext_arrays: bool = Field(description="whether to encode outputs")


class GetModelsHealth(BaseModel):
    identifier:str
    is_alive: bool


class DeployRequest(BaseModel):
    """Request model for model deployment"""
    identifier: str = ""
    model_name: str = ""
    model_path: Optional[str] = None
    decoder_path: Optional[str] = None
    model_type: str = ""
    disable_gpu: Optional[bool] = True
    batch_size: int = ""
    max_input: int = ""
    transformers_cache: Optional[str] = "../.cache"
    model_class: str = ""
    return_plaintext_arrays: Optional[bool] = False
    preloaded_adapters: Optional[bool] = True


class DeployResult(BaseModel):
    """Response model for model deployment"""
    success: bool = Field(..., description="True if the deployment is successful")
    container: str = Field(..., description="The id of the container where the model is deployed")
    message: str = Field(..., description="Error or success message")


class RemoveResult(BaseModel):
    """Response model for model removal"""
    success: bool = Field(..., description="True if the model removal is successful")
    message: str = Field(..., description="Error or success message")


class UpdateModel(BaseModel):
    disable_gpu: Optional[bool] = None
    batch_size: Optional[int] = None
    max_input: Optional[int] = None
    return_plaintext_arrays: Optional[bool] = None
