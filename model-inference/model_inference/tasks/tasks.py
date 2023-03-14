import logging
from abc import ABC

from celery import Task

from .celery import app
from .config.model_config import model_config
from .models.request import PredictionRequest


logger = logging.getLogger(__name__)


class ModelTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support providing mongo client.
    """

    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def _create_model_instance(self):
        """
        Create a new model instance based on the `model_type` configuration.
        """
        model_config.update()
        logger.info(f"Configuration: {model_config}")
        model_type = model_config.model_type
        if model_type == "transformer":
            from .inference.transformer import Transformer

            return Transformer()
        elif model_type == "adapter":
            from .inference.adaptertransformer import AdapterTransformer

            return AdapterTransformer()
        elif model_type == "sentence-transformer":
            from .inference.sentencetransformer import SentenceTransformer

            return SentenceTransformer()
        elif model_type == "onnx":
            from .inference.onnx import Onnx

            return Onnx()
        elif model_type == "graph":
            from .inference.graph_transformers import GraphTransformers

            return GraphTransformers()
        elif model_type == "metaqa":
            from .inference.metaqa import MetaQA

            return MetaQA()
        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def __call__(self, *args, **kwargs):
        """
        Instantiate mongo client on first call (i.e. first task processed)
        Avoids the creation of multiple clients for each task request
        """

        if not self.model:
            logger.info(model_config)
            model_instance = self._create_model_instance()
            self.model = model_instance
        return self.run(*args, **kwargs)


@app.task(
    bind=True,
    base=ModelTask,
)
def prediction_task(self, prediction_request, task, model_config):
    # TODO: possibly remove sending model_config as a parameter
    logger.info(f"Prediction Request: {prediction_request} for task {task}")
    prediction = self.model.predict(PredictionRequest(**prediction_request), task)
    logger.info(f"Prediction: {prediction}")
    return prediction.dict()
