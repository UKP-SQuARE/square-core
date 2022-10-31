import ast
import asyncio
import base64
import json
import logging
import time
import os
from io import BytesIO

import aiohttp
import numpy as np
import requests
from aiohttp.client import ClientSession
from square_auth.client_credentials import ClientCredentials

from ..models.index import Index
logger = logging.getLogger(__name__)

client_credentials = ClientCredentials()

class ModelAPIClient:
    """Wraps access to Square Model API methods used in the Datastore API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.square_api_url = base_url
        self.verify_ssl = os.getenv("VERIFY_SSL", "1") == "1"
        self.max_attempts = 50
        self.poll_interval = 2
        

    def is_alive(self, index: Index, credential_token: str) -> bool:
        if not self.base_url:
            raise EnvironmentError("Model API not available.")

        if credential_token is None:
            raise ValueError("Credential token is None")

        if index.query_encoder_model is None:
            return False

        request_url = f"{self.base_url}/{index.query_encoder_model}/health/heartbeat"
        try:
            response = requests.get(
                request_url, 
                headers={"Authorization": f"Bearer {credential_token}"}
            )
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

    async def encode_query(self, query: str, index: Index, credential_token: str):
        if index.query_encoder_model is None:
            return None
        if not self.base_url:
            raise EnvironmentError("Model API not available.")

        data = {
            "input": [query],
            "adapter_name": index.query_encoder_adapter,
            "task_kwargs": {
                "embedding_mode": index.embedding_mode
            }
        }

        response = await self.predict(
            model_identifier=index.query_encoder_model, 
            prediction_method="embedding", 
            input_data=data
        )
        logger.info(f"Model API response={response}")

        embeddings = self._decode_embeddings(
            response["model_outputs"]["embeddings"]
        ).flatten()
        # The vector returned here may be shorter than the stored document vector.
        # In that case, we fill the remaining values with zeros.
        if index.embedding_size - len(embeddings) > 0:
            logger.warning(
                "Embedded query vector is shorter than the configured size."
            )
        return embeddings.tolist() + [0] * (index.embedding_size - len(embeddings))

    async def _wait_for_task(
        self,
        task_id: str,
        session: ClientSession,
        max_attempts=None,
        poll_interval=None,
    ):
        """
        Handling waiting for a task to finish. While the task has
        not finished request the result from the task_result
        endpoint and check whether it is finished
        Args:
             task_id (str): the id of the task
             max_attempts (int, optional): the maximum number of
                attempts to get the result. If this is None the
                self.max_attempts is used. The default is None.
             poll_interval (int, optional): the interval between the
                attempts to poll the results. If this is None
                self.poll_intervall is used. Defaults to None.
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        if poll_interval is None:
            poll_interval = self.poll_interval
        attempts = 0
        result = None
        while attempts < max_attempts:
            attempts += 1
            async with session.get(
                url=f"{self.square_api_url}/task_result/{task_id}",
                headers={"Authorization": f"Bearer {client_credentials()}"},
                verify_ssl=self.verify_ssl,
            ) as response:
                resp = await response.text()

                if response.status == 200:
                    result = ast.literal_eval(json.dumps(resp))
                    break
                time.sleep(poll_interval)
        return json.loads(result)["result"]

    async def predict(self, model_identifier, prediction_method, input_data):
        """
        Request model prediction.
        Args:
            model_identifier (str): the identifier of the model that
                should be used for the prediction
            prediction_method (str): what kind of prediction should
                be made. Possible values are embedding,
                sequence-classification, token-classification,
                generation, question-answering
            input_data (Dict): the input for the prediction
        """
        supported_prediction_methods = [
            "embedding",
            "sequence-classification",
            "token-classification",
            "generation",
            "question-answering",
        ]
        if prediction_method not in supported_prediction_methods:
            raise ValueError(
                f"Unknown prediction_method {prediction_method}. "
                f"Please choose one of the following "
                f"{supported_prediction_methods}"
            )

        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.post(
                url=f"{self.square_api_url}/{model_identifier}/{prediction_method}",
                json=input_data,
                headers={"Authorization": f"Bearer {client_credentials()}"},
                verify_ssl=self.verify_ssl,
            ) as response:

                result = await response.text()
                # print(response, flush=True)
                if response.status == 200:
                    return await asyncio.ensure_future(
                        self._wait_for_task(
                            ast.literal_eval(result)["task_id"],
                            session=session,
                        )
                    )
                else:
                    return response
