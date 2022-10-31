import logging

import torch
from sentence_transformers import \
    SentenceTransformer as SentenceTransformerModel
from tasks.config.model_config import model_config
from tasks.inference.model import Model
from tasks.models.prediction import (PredictionOutput,
                                     PredictionOutputForEmbedding)
from tasks.models.request import PredictionRequest, Task

logger = logging.getLogger(__name__)


class SentenceTransformer(Model):
    """
    The class for all sentence-transformers models
    """

    def __init__(self, **kwargs):
        """
        Initialize the SentenceTransformer

        Args:

             model_name: the sentence-transformer model name (https://sbert.net/docs/pretrained_models.html)
             disable_gpu: do not move model to GPU even if CUDA is available
             kwargs: Not used
        """
        self._load_model(model_config.model_name, model_config.disable_gpu)

    def _load_model(self, model_name, disable_gpu):
        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.

        Args:

             model_name: the sentence-transformer model name (https://sbert.net/docs/pretrained_models.html)
             disable_gpu: do not move model to GPU even if CUDA is available
        """
        logger.debug(f"Loading model {model_name}")
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = SentenceTransformerModel(model_name_or_path=model_name, device=device)
        logger.info(f"Model {model_name} loaded on {device}")
        self.model = model

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        embeddings = self.model.encode(
            request.input, batch_size=model_config.batch_size, show_progress_bar=False
        )
        return PredictionOutputForEmbedding(model_outputs={"embeddings": embeddings})

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        """
        Args:

             request: the prediction request
             task: task for which the prediction is required (e.g. embedding)
        """
        if request.is_preprocessed:
            raise ValueError(
                "is_preprocessed=True is not supported for this model. Please use text as input."
            )
        if len(request.input) > model_config.max_input_size:
            raise ValueError(
                f"Input is too large. Max input size is {model_config.max_input_size}"
            )
        if task != Task.embedding:
            raise ValueError("Only embedding task supported by this model")
        return self._embedding(request)
