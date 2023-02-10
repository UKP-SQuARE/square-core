import base64
from io import BytesIO

import numpy as np
import torch
from starlette.config import Environ
from model_inference.tasks.models.prediction import PredictionOutput, _encode_numpy


def test_prediction_output_numpy_encoded() -> None:

    arr = np.ones(shape=(10, 10), dtype="float32")
    output = _encode_numpy({"test": torch.from_numpy(arr)}, return_plaintext=False)
    encoded_arr = output["test"]

    # reversing code
    arr_binary_b64 = encoded_arr.encode()
    arr_binary = base64.decodebytes(arr_binary_b64)
    arr_back = np.load(BytesIO(arr_binary))

    np.testing.assert_equal(arr, arr_back)


def test_prediction_output_numpy_plaintext() -> None:

    arr = np.ones(shape=(10, 10), dtype="float32")
    output = _encode_numpy({"test": torch.from_numpy(arr)}, return_plaintext=True)
    plaintext_list_arr = output["test"]
    # reversing code
    arr_back = np.array(plaintext_list_arr)

    np.testing.assert_equal(arr, arr_back)
