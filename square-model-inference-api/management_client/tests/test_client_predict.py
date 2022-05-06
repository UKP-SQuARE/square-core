import unittest
import os

from client.client import ManagementClient
import base64
import numpy as np
from io import BytesIO
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


class TestClientPredict(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = ManagementClient("https://localhost:8443",
                                      client_secret=CLIENT_SECRET,
                                      verify_ssl=False)
        identifier = "bert_adapter_test"
        model_attributes = {
            "identifier": identifier,
            "model_name": "bert-base-uncased",
            "model_type": "adapter",
            "disable_gpu": True,
            "batch_size": 32,
            "max_input": 1024,
            "transformers_cache": "../.cache",
            "model_class": "generation",
            "return_plaintext_arrays": False,
            "preloaded_adapters": False
        }
        cls.client.deploy(model_attributes)
        identifier = "gpt2_test"
        model_attributes = {
            "identifier": identifier,
            "model_name": "bert-base-uncased",
            "model_type": "transformer",
            "disable_gpu": True,
            "batch_size": 32,
            "max_input": 1024,
            "transformers_cache": "../.cache",
            "model_class": "generation",
            "return_plaintext_arrays": False,
            "preloaded_adapters": True
        }
        cls.client.deploy(model_attributes)

    def test_client_embedding(self):
        result = self.client.predict("facebook-dpr-question_encoder-single-nq-base",
                                     input_data={"input": ["Some text"]}, prediction_method="embedding")
        self.assertTrue("model_outputs" in result)
        self.assertTrue("embeddings" in result["model_outputs"])
        self.assertEquals(type(result["model_outputs"]["embeddings"]), str)

    def test_client_sequence_classification(self):
        identifier = "bert_adapter_test"
        result = self.client.predict(identifier,
                                     input_data={
                                            "input": [["What is a test?", "A test is a thing where you test."]],
                                            "adapter_name": "lingaccept/cola@ukp"
                                     },
                                     prediction_method="embedding")
        self.assertTrue("logits" in result["model_outputs"])
        self.assertEqual(type(result["model_outputs"]["logits"]), str)

        arr_binary_b64 = result["model_outputs"]["logits"].encode()
        arr_binary = base64.decodebytes(arr_binary_b64)
        arr = np.load(BytesIO(arr_binary))

        self.assertEquals(arr.shape, (1, 2))

    def test_client_token_classification(self):
        identifier = "bert_adapter_test"
        result = self.client.predict(identifier,
                                     input_data={"input": ["Some text"], "adapter_name": "ner/conll2003@ukp"},
                                     prediction_method="token-classification")
        self.assertTrue("logits" in result["model_outputs"])
        self.assertEqual(type(result["model_outputs"]["logits"]), str)

        arr_binary_b64 = result["model_outputs"]["logits"].encode()
        arr_binary = base64.decodebytes(arr_binary_b64)
        arr = np.load(BytesIO(arr_binary))

        self.assertEquals(arr.shape, (1, 4, 9))

    def test_client_question_answering(self):
        identifier = "bert_adapter_test"
        result = self.client.predict(identifier,
                                     input_data={
                                         "input": [["What is a test?", "A test is a thing where you test."]],
                                         "adapter_name": "qa/squad1@ukp"
                                     },
                                     prediction_method="question-answering")
        self.assertTrue("start_logits" in result["model_outputs"])
        self.assertEqual(type(result["model_outputs"]["start_logits"]), str)

        arr_binary_b64 = result["model_outputs"]["start_logits"].encode()
        arr_binary = base64.decodebytes(arr_binary_b64)
        arr = np.load(BytesIO(arr_binary))

        self.assertEquals(arr.shape, (1, 17))

    def test_client_generation(self):
        identifier = "gpt2_test"
        result = self.client.predict(identifier, input_data={"input": ["Some text"]}, prediction_method="generation")
        self.assertTrue("model_outputs" in result)
        self.assertTrue("sequences" in result["model_outputs"])


if __name__ == '__main__':
    unittest.main()
