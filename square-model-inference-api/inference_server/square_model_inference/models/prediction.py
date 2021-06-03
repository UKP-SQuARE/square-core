import torch
from io import BytesIO
import base64
import numpy as np
from pydantic import Field, BaseModel
from square_model_inference.core.config import RETURN_PLAINTEXT_ARRAYS

def _encode_numpy(obj):
    def encode(arr):
        if RETURN_PLAINTEXT_ARRAYS:
            return arr.tolist()
        else:
            with BytesIO() as b:
                np.save(b, arr)
                arr_binary = b.getvalue()
            arr_binary_b64 = base64.b64encode(arr_binary)
            arr_string_b64 = arr_binary_b64.decode("latin1")
            return arr_string_b64
            # LOADING WITH
            # arr_binary_b64 = arr_string_b64.encode()
            # arr_binary = base64.decodebytes(arr_binary_b64)
            # arr = np.load(BytesIO(arr_binary))
    for k, v in obj.items():
        if isinstance(v, torch.Tensor):
            v = v.numpy()
            obj[k] = encode(v)
        elif isinstance(v, tuple) and isinstance(v[0], torch.Tensor):
            v = [encode(vv.numpy()) for vv in v]
            obj[k] = v
    return obj


class PredictionOutput(BaseModel):
    """
    The results of the prediction of the model on the given input for the requested task.
    """
    model_outputs: dict = Field(
        description="Dictionary containing the model outputs as numpy arrays cast to lists."
    )
    task_outputs: dict = Field(
        description="Dictionary containing the task outputs. This covers anything from generated text, "
                    "id2label mappings, token2word mappings, etc."
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.model_outputs = _encode_numpy(self.model_outputs)

