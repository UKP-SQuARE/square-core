from typing import Optional

from pydantic import BaseModel


class ModelRequest(BaseModel):
    identifier: str
    model_name: str
    model_path: Optional[str] = None
    decoder_path: Optional[str] = None
    model_type: str
    disable_gpu: Optional[bool] = True
    batch_size: int
    max_input: int
    transformers_cache: Optional[str] = "../.cache"
    model_class: str
    return_plaintext_arrays: Optional[bool] = False
    preloaded_adapters: Optional[bool] = True
