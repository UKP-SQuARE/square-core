import os
import unittest

from model_inference.app.models.request import PredictionRequest
from model_inference.tasks.models.request import Task
from model_inference.tasks.tasks import prediction_task


TEST_MODEL_PATH = os.getenv("TEST_MODEL_PATH", "./model4test")


class TestTasks(unittest.TestCase):
    def test_embedding_task(self):
        request = PredictionRequest(input=["Some text"], adapter_name="lingaccept/cola@ukp")
        task = Task.embedding
        model_config = {
            "identifier": "test_config",
            "model_type": "adapter",
            "model_name": TEST_MODEL_PATH,
            "disable_gpu": False,
            "batch_size": 32,
            "max_input": 1024,
            "model_class": "base",
            "return_plaintext_arrays": False,
            "preloaded_adapters": False,
        }
        rst = prediction_task(request.dict(), task, model_config)
        self.assertEqual(rst["embedding_mode"], "mean")
        self.assertEqual(len(rst["model_outputs"]["embeddings"][0]), 768)

    def test_seq_task(self):
        adapter_name = "lingaccept/cola@ukp"
        request = PredictionRequest(input=["Some text"], adapter_name=adapter_name)
        task = Task.sequence_classification
        model_config = {
            "identifier": "test_config",
            "model_type": "adapter",
            "model_name": TEST_MODEL_PATH,
            "disable_gpu": False,
            "batch_size": 32,
            "max_input": 1024,
            "model_class": "base",
            "return_plaintext_arrays": False,
            "preloaded_adapters": False,
        }
        rst = prediction_task(request.dict(), task, model_config)
        self.assertEqual(len(rst["model_outputs"]["logits"][0]), 2)

    def test_token_task(self):
        adapter_name = "ner/conll2003@ukp"
        request = PredictionRequest(input=["Some text"], adapter_name=adapter_name)
        task = Task.token_classification
        model_config = {
            "identifier": "test_config",
            "model_type": "adapter",
            "model_name": TEST_MODEL_PATH,
            "disable_gpu": False,
            "batch_size": 32,
            "max_input": 1024,
            "model_class": "base",
            "return_plaintext_arrays": False,
            "preloaded_adapters": False,
        }
        rst = prediction_task(request.dict(), task, model_config)
        self.assertEqual(len(rst["model_outputs"]["logits"][0]), 4)
        self.assertEqual(len(rst["model_outputs"]["logits"][0][0]), 9)

    def test_question_answering_task(self):
        adapter_name = "qa/squad1@ukp"
        request = PredictionRequest(
            input=[["What is a test?", "A test is a thing where you test."]],
            adapter_name=adapter_name,
        )
        task = Task.question_answering
        model_config = {
            "identifier": "test_config",
            "model_type": "adapter",
            "model_name": TEST_MODEL_PATH,
            "disable_gpu": False,
            "batch_size": 32,
            "max_input": 1024,
            "model_class": "base",
            "return_plaintext_arrays": False,
            "preloaded_adapters": False,
        }
        rst = prediction_task(request.dict(), task, model_config)
        self.assertEqual(len(rst["model_outputs"]["start_logits"][0]), 17)
        self.assertEqual(len(rst["model_outputs"]["end_logits"][0]), 17)
