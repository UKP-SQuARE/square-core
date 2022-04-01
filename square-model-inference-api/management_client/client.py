from time import sleep

import requests
import os
from square_auth.client_credentials import ClientCredentials

REALM = os.getenv("REALM")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")

class ManagementClient:
    """
    This client provides an easy interface to the model-api from the square project.
    It handles authentication, sends the requests and for those that only return the task id it
    waits until the results are computed
    """

    def __init__(
            self,
            api_url,
            client_secret,
            verify_ssl=True,
            keycloak_base_url="https://square.ukp-lab.de",
            realm="Models-test",
            client_id="models",
    ):
        """
        This method initializes the client and the credentials which will be needed for each access.
        Args:
            api_url (str): The base url of the model-api
            client_secret (str): The secret of the client needed for authentication
            verify_ssl (bool): Whether the ssl should be verified
            keycloak_base_url (str): the base url of the keycloak server
            realm (str): the realm used by the client credentials
            client_id (str): the client id used by the client credentials
        """
        self.url = api_url
        self.client_credentials = ClientCredentials(keycloak_base_url, realm, client_id, client_secret)
        self.verify_ssl = verify_ssl
        self.max_attempts = 50
        self.poll_interval = 20

    def _wait_for_task(self, identifier, task_id, max_attempts=None, poll_interval=None):
        """
        Handling waiting for a task to finish. While the task has not finished request the result from
        the task_result endpoint and check whether it is finished
        Args:
             identifier (str): the identifier of the container which queued the task
             task_id (str): the id of the task
             max_attempts (int, optional): the maximum number of attempts to get the result. If this is None the
                self.max_attempts is used. The default is None.
             poll_interval (int, optional): the interval between the attempts to poll the results. If this is None
                self.poll_intervall is used. Defaults to None.
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        if poll_interval is None:
            poll_interval = self.poll_interval
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            result_response = requests.get(
                url="{}/api/{}/task_result/{}".format(self.url, identifier, task_id),
                headers={"Authorization": f"Bearer {self.client_credentials()}"},
                verify=self.verify_ssl,
            )
            if result_response.status_code == 200:
                result = result_response.json()["result"]
                break
            sleep(poll_interval)
        return result

    def predict(self, model_identifier, prediction_method, input_data):
        """
        Request model prediction.
        Args:
            model_identifier (str): the identifier of the model that should be used for the prediction
            prediction_method (str): what kind of prediction should be made. Possible values are embedding,
                sequence-classification, token-classification, generation, question-answering
            input_data (Dict): the input for the prediction
        """
        supported_prediction_methods = ["embedding", "sequence-classification", "token-classification," "generation",
                                        "question-answering"]
        if prediction_method not in supported_prediction_methods:
            raise ValueError(
                f"Unknown prediction_method {prediction_method}. Please choose one of the following {supported_prediction_methods}")
        response = requests.post(
            url="{}/api/{}/{}".format(self.url, model_identifier, prediction_method),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            json=input_data,
            verify=self.verify_ssl,
        )
        if response.status_code == 200:
            return self._wait_for_task(model_identifier, response.json()["task_id"])
        else:
            return response

    def stats(self, model_identifier):
        """
        Get the statistics from the model with the given identifier
        Args:
            model_identifier(str): the identifier of the model to provide the statistics for
        """
        response = requests.get(
            url="{}/api/{}/stats".format(self.url, model_identifier),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    def deployed_models(self):
        """
        Get all deployed models and their statistics
        """
        response = requests.get(
            url="{}/api/models/deployed-models-health".format(self.url),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    def deployed_models_health(self):
        """
        Get all deployed models and their health status
        """
        response = requests.get(
            url="{}/api/models/deployed-models-health".format(self.url),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        return response.json()

    def deploy(self, model_attributes):
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
        response = requests.post(
            url="{}/api/models/deploy".format(self.url),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            json=model_attributes,
            verify=self.verify_ssl,
        )
        if response.status_code == 200:
            return self._wait_for_task("models", response.json()["task_id"])
        else:
            return response

    def remove(self, model_identifier):
        """
        Remove the model with the given identifier
        Args:
            model_identifier (str): the identifier of the model that should be removed
        """
        response = requests.post(
            url="{}/api/models/remove/{}".format(self.url, model_identifier),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            verify=self.verify_ssl,
        )
        if response.status_code == 200:
            return self._wait_for_task("models", response.json()["task_id"])
        else:
            return response

    def update(self, model_identifier, updated_attributes):
        """
        Updating the attributes of a deployed model. Note that only disable_gpu, batch_size,
        max_input, return_plaintext_arrays can be changed.
        Args:
            model_identifier (str): the identifier of the model that should be updated
            updated_attributes (Dict): the new attributes of the model.
                An example could look like this:
                {
                    "disable_gpu": True,
                    "batch_size": 32,
                    "max_input": 256,
                    "return_plaintext_arrays": True
                }
        """
        response = requests.post(
            url="{}/api/models/update/{}".format(self.url, model_identifier),
            headers={"Authorization": f"Bearer {self.client_credentials()}"},
            json=updated_attributes,
            verify=self.verify_ssl,
        )
        return response.json()
