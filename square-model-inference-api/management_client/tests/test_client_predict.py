import unittest

from client import ManagementClient


class TestClientPredict(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ManagementClient("https://localhost:8443", client_secret="vtioWa2MvU4YaZltaL5tFjGMkMVhbnoQ",
                                       verify_ssl=False)

    def test_client_embedding(self):
        result = self.client.predict("facebook-dpr-question_encoder-single-nq-base",
                                     input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertTrue("model_outputs" in result)
        self.assertTrue("embeddings" in result["model_outputs"])
        self.assertEquals(type(result["model_outputs"]["embeddings"]), str)

    def test_deployed_models(self):
        result = self.client.deployed_models()
        self.assertTrue(any(model["identifier"] == "facebook-dpr-question_encoder-single-nq-base" for model in result))

    def test_deployed_models_health(self):
        result = self.client.deployed_models_health()
        self.assertTrue(any(
            model["identifier"] == "facebook-dpr-question_encoder-single-nq-base" and model["is_alive"] is True for
            model in result))

    def test_deploy_and_remove(self):
        model_attributes = {
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
        result_deploy = self.client.deploy(model_attributes)
        self.assertTrue(result_deploy["success"])
        models = self.client.deployed_models_health()
        self.assertTrue(any(model["identifier"] == "bert" and model["is_alive"] is True for model in models))

        result_remove = self.client.remove("bert")
        self.assertTrue(result_remove["success"])
        models = self.client.deployed_models_health()
        self.assertFalse(any(model["identifier"] == "bert" for model in models))

    def test_update(self):
        updated_params = {
            "disable_gpu": True,
            "batch_size": 32,
            "max_input": 256,
            "return_plaintext_arrays": True
        }
        result = self.client.update("facebook-dpr-question_encoder-single-nq-base", updated_params)
        self.assertTrue(result["content"]["return_plaintext_arrays"])
        prediction_result = self.client.predict("facebook-dpr-question_encoder-single-nq-base",
                                                input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertEquals(type(prediction_result["model_outputs"]["embeddings"]), list)

        updated_params["return_plaintext_arrays"] = False
        result = self.client.update("facebook-dpr-question_encoder-single-nq-base", updated_params)
        self.assertFalse(result["content"]["return_plaintext_arrays"])

        prediction_result = self.client.predict("facebook-dpr-question_encoder-single-nq-base",
                                                input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertEquals(type(prediction_result["model_outputs"]["embeddings"]), str)


if __name__ == '__main__':
    unittest.main()
