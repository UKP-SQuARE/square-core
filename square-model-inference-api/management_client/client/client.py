import json
import time

import requests
import os
import ast
from square_auth.client_credentials import ClientCredentials

import asyncio
import aiohttp
from aiohttp.client import ClientSession

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REALM = os.getenv("REALM")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")


class ManagementClient:
    """
    This client provides an easy interface to the model-api
    from the square project.
    It handles authentication, sends the requests and for
    those that only return the task id it
    waits until the results are computed
    """

    def __init__(
            self,
            api_url,
            client_secret,
            verify_ssl=True,
            keycloak_base_url="https://square.ukp-lab.de",
            realm="square",
            client_id="models",
    ):
        """
        This method initializes the client and the credentials which
        will be needed for each access.
        Args:
            api_url (str): The base url of the model-api
            client_secret (str): The secret of the client needed for authentication
            verify_ssl (bool): Whether the ssl should be verified
            keycloak_base_url (str): the base url of the keycloak server
            realm (str): the realm used by the client credentials
            client_id (str): the client id used by the client credentials
        """
        self.url = api_url
        self.client_credentials = ClientCredentials(
            keycloak_base_url,
            realm,
            client_id,
            client_secret
        )
        self.verify_ssl = verify_ssl
        self.max_attempts = 50
        self.poll_interval = 2

    async def _wait_for_task(self, task_id: str,
                             session: ClientSession,
                             max_attempts=None,
                             poll_interval=None):
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
                    url=f"{self.url}/api/main/task_result/{task_id}",
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
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
        supported_prediction_methods = ["embedding",
                                        "sequence-classification",
                                        "token-classification",
                                        "generation",
                                        "question-answering"]
        if prediction_method not in supported_prediction_methods:
            raise ValueError(
                f"Unknown prediction_method {prediction_method}. "
                f"Please choose one of the following "
                f"{supported_prediction_methods}")

        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.post(
                    url=f"{self.url}/api/main/{model_identifier}/{prediction_method}",
                    json=input_data,
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
                result = await response.text()
                # print(response.status)
                if response.status == 200:
                    return await asyncio.ensure_future(self._wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session,
                    ))
                else:
                    return response

    def stats(self, model_identifier):
        """
        Get the statistics from the model with the given identifier
        Args:
            model_identifier(str): the identifier of the model
                to provide the statistics for
        """
        response = requests.get(
            url="{}/api/main/{}/stats".format(self.url, model_identifier),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    def deployed_models(self):
        """
        Get all deployed models and their statistics
        """
        response = requests.get(
            url="{}/api/models/deployed-models".format(self.url),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    def deployed_model_workers(self):
        """
        Get all deployed models and their statistics
        """
        response = requests.get(
            url="{}/api/models/deployed-model-workers".format(self.url),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    async def deploy(self, model_attributes):
        """
        Deploy a new model.
        Args:
            model_attributes (Dict): the attributes of the deployed models.
                An example would be:
                {
                    "identifier": "bert",
                    "model_name": "bert-base-uncased",
                    "model_type": "transformer",
                    "disable_gpu": True,
                    "batch_size": 32,
                    "max_input": 1024,
                    "transformers_cache": "../.cache",
                    "model_class": "base",
                    "return_plaintext_arrays": False,
                    "preloaded_adapters": True
                }
        """
        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.post(
                    url=f"{self.url}/api/models/deploy",
                    json=model_attributes,
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
                result = await response.text()
                # print(response.status)
                if response.status == 200:
                    return await asyncio.ensure_future(self._wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session,
                        poll_interval=20
                    ))
                else:
                    return response

    async def remove(self, model_identifier):
        """
        Remove the model with the given identifier
        Args:
            model_identifier (str): the identifier of the model that should be removed
        """
        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.delete(
                    url=f"{self.url}/api/models/remove/{model_identifier}",
                    json=model_identifier,
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
                result = await response.text()
                # print(response.status)
                if response.status == 200:
                    return await asyncio.ensure_future(self._wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session
                    ))
                else:
                    return response

    def update(self, model_identifier, updated_attributes):
        """
        Updating the attributes of a deployed model. Note that
        only disable_gpu, batch_size,
        max_input, return_plaintext_arrays can be changed.
        Args:
            model_identifier (str): the identifier of the model
                that should be updated
            updated_attributes (Dict): the new attributes of the model.
                An example could look like this:
                {
                    "disable_gpu": True,
                    "batch_size": 32,
                    "max_input": 256,
                    "return_plaintext_arrays": True
                }
        """
        response = requests.patch(
            url="{}/api/models/update/{}".format(self.url, model_identifier),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            json=updated_attributes,
            verify=self.verify_ssl,
        )
        return response.json()

    async def add_worker(self, model_identifier, number):
        """
        Adds workers of a specific model such that heavy
        workloads can be handled better.
        Note, that only the creater of the model is allowed to add
        new workers and only admins are allowed to have more than 2
        workers for each model.
        Args:
            model_identifier (str): the identifier of the model
                to add workers for
            number (int): the number of workers to add
        """

        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.patch(
                    url=f"{self.url}/api/models/{model_identifier}/add_worker/{number}",
                    json=model_identifier,
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
                result = await response.text()
                if response.status == 200:
                    return await asyncio.ensure_future(self._wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session
                    ))
                else:
                    return response

    async def remove_worker(self, model_identifier, number):
        """
        Remove/down-scale model worker
        """

        my_conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=my_conn) as session:
            async with session.patch(
                    url=f"{self.url}/api/models/{model_identifier}/remove_worker/{number}",
                    json=model_identifier,
                    headers={"Authorization": f"Bearer {self.client_credentials()}"},
                    verify_ssl=self.verify_ssl) as response:
                result = await response.text()
                if response.status == 200:
                    return await asyncio.ensure_future(self._wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session
                    ))
                else:
                    return response
