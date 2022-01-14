import base64
import logging
from io import BytesIO
from urllib import request

import numpy as np
import requests

from ..models.index import Index


logger = logging.getLogger(__name__)


class ModelAPIClient:
    """Wraps access to Square Model API methods used in the Datastore API."""

    def __init__(self, base_url: str, model_api_user: str, model_api_password: str):
        self.base_url = base_url
        self.auth = (model_api_user, model_api_password)

    def is_alive(self, index: Index) -> bool:
        if not self.base_url:
            raise EnvironmentError("Model API not available.")
        if index.query_encoder_model is None:
            return False

        request_url = f"{self.base_url}/{index.query_encoder_model}/health/heartbeat"
        try:
            response = requests.get(request_url, auth=self.auth)
            if response.status_code != 200:
                return False
            else:
                return response.json().get("is_alive", False)
        except Exception:
            return False

    def _decode_embeddings(self, encoded_string: str):
        encoded_string = encoded_string.encode()
        arr_binary = base64.decodebytes(encoded_string)
        arr = np.load(BytesIO(arr_binary))
        return arr

    def encode_query(self, query: str, index: Index):
        if index.query_encoder_model is None:
            return None
        if not self.base_url:
            raise EnvironmentError("Model API not available.")

        request_url = f"{self.base_url}/{index.query_encoder_model}/embedding"
        data = {
            "input": [query],
            "adapter_name": index.query_encoder_adapter,
        }
        logger.info(f"{request_url} : {data}")
        response = requests.post(request_url, json=data, auth=self.auth)
        if response.status_code != 200:
            logger.error(response.json())
            raise EnvironmentError(f"Model API returned {response.status_code}.")
        else:
            embeddings = self._decode_embeddings(
                response.json()["model_outputs"]["embeddings"]
            ).flatten()
            # The vector returned here may be shorter than the stored document vector.
            # In that case, we fill the remaining values with zeros.
            if index.embedding_size - len(embeddings) > 0:
                logger.warning(
                    "Embedded query vector is shorter than the configured size."
                )
            return embeddings.tolist() + [0] * (index.embedding_size - len(embeddings))
