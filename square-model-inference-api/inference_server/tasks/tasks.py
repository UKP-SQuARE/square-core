import logging
import os
from abc import ABC

from celery import Task

from .celery import app
from .config.model_config import model_config
from .inference.adaptertransformer import AdapterTransformer
from .inference.onnx import Onnx
from .inference.sentencetransformer import SentenceTransformer
from .inference.transformer import Transformer
from .models.request import PredictionRequest

logger = logging.getLogger(__name__)

MODEL_MAPPING = {
    "adapter": AdapterTransformer,
    "transformer": Transformer,
    "sentence-transformer": SentenceTransformer,
    "onnx": Onnx,
}

IDENTIFIER = os.getenv("QUEUE")


class ModelTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support providing mongo client.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Instantiate mongo client on first call (i.e. first task processed)
        Avoids the creation of multiple clients for each task request
        """
        model_config.update(IDENTIFIER)
        logger.info(f"Configuration: {model_config}")
        if not self.model:
            logger.info(model_config)
            model_instance = MODEL_MAPPING[model_config.model_type]()
            self.model = model_instance
        return self.run(*args, **kwargs)


@app.task()
def add_two(x, y):
    return x + y


@app.task(
    bind=True,
    base=ModelTask,
)
def prediction_task(self, prediction_request, task, model_config):
    logger.info(f"Prediction Request: {prediction_request} for task {task}")
    logger.info(model_config)
    prediction = self.model.predict(PredictionRequest(**prediction_request), task)
    return prediction.dict()

