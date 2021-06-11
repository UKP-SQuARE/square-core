from typing import Dict, Union, Tuple

import torch
from io import BytesIO
import base64
import numpy as np
from pydantic import Field, BaseModel
from square_model_inference.core.config import RETURN_PLAINTEXT_ARRAYS


def _encode_numpy(obj: Dict[str, Union[torch.Tensor, Tuple[torch.Tensor]]], return_plaintext: bool=RETURN_PLAINTEXT_ARRAYS) -> Dict[str, Union[list, str]]:
    """
    Encodes the Torch Tensors first to Numpy arrays and then makes either plain lists or base64-encode them depending
    on the flag RETURN_PLAINTEXT_ARRAYS
    :param obj: the objects whose tensors will be encoded
    :return: the same dictionary with all tensors replaced by lists or base64-encoded array strings.
    """
    def encode(arr):
        if return_plaintext:
            return arr.tolist()
        else:
            # np.save expects a file which we emulate with BytesIO
            with BytesIO() as b:
                np.save(b, arr)
                arr_binary = b.getvalue()
            arr_binary_b64 = base64.b64encode(arr_binary)
            arr_string_b64 = arr_binary_b64.decode("latin1")
            return arr_string_b64
            # DECODE THE VALUE WITH
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
        description="Dictionary containing the model tensor outputs either as plain list or as base64-encoded numpy array."
    )
    task_outputs: dict = Field(
        description="Dictionary containing the task outputs. This covers anything from generated text, "
                    "labels, id2label mappings, token2word mappings, etc."
    )

    def __init__(self, **data):
        """
        Data model for the model and task outputs.
        The model outputs (,i.e., tensors) will be encoded as base64 strings or as plain lists depending on the flag
        RETURN_PLAINTEXT_ARRAYS.
        :param data:
        'model_outputs': dict[str: Union[torch.Tensor, Tuple[torch.Tensor]]]. All tensor results of the model
        'task_outputs': dict[str: Any]. All non-tensor results of the processed task like the predicted labels, extracted spans, etc.
        """
        super().__init__(**data)
        self.model_outputs = _encode_numpy(self.model_outputs)

