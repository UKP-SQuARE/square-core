import unittest

from client.client import ManagementClient
import os

CLIENT_SECRET = os.getenv("CLIENT_SECRET")


class TestClientMaintaining(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ManagementClient("https://localhost:8443",
                                       client_secret=CLIENT_SECRET,
                                       verify_ssl=False)

    def test_deployed_models(self):
        result = self.client.deployed_models()
        self.assertTrue(any(model["identifier"] == "facebook-dpr-question_encoder-single-nq-base" for model in result))

    def test_deploy_and_remove(self):
        identifier="bert-test"
        model_attributes = {
            "identifier": identifier,
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
        result_deploy = self.client.deploy(model_attributes)
        self.assertTrue(result_deploy["success"])
        models = self.client.deployed_models()
        self.assertTrue(any(model["identifier"] == identifier for model in models))

        result_remove = self.client.remove(identifier)
        self.assertTrue(result_remove["success"])
        models = self.client.deployed_models()
        self.assertFalse(any(model["identifier"] == identifier for model in models))

    def test_update(self):
        identifier = "bert-test"
        model_attributes = {
            "identifier": identifier,
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
        result_deploy = self.client.deploy(model_attributes)
        self.assertTrue(result_deploy["success"])
        models = self.client.deployed_models()
        self.assertTrue(any(model["identifier"] == identifier for model in models))

        updated_params = {
            "disable_gpu": True,
            "batch_size": 32,
            "max_input": 256,
            "return_plaintext_arrays": True
        }
        result = self.client.update(identifier, updated_params)
        self.assertTrue(result["content"]["return_plaintext_arrays"])
        prediction_result = self.client.predict(identifier,
                                                input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertEquals(type(prediction_result["model_outputs"]["embeddings"]), list)

        updated_params["return_plaintext_arrays"] = False
        result = self.client.update(identifier, updated_params)
        self.assertFalse(result["content"]["return_plaintext_arrays"])

        prediction_result = self.client.predict(identifier,
                                                input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertEquals(type(prediction_result["model_outputs"]["embeddings"]), str)
        result_remove = self.client.remove(identifier)
        self.assertTrue(result_remove["success"])
        models = self.client.deployed_models()
        self.assertFalse(any(model["identifier"] == identifier for model in models))


if __name__ == '__main__':
    unittest.main()
