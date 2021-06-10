import json
from typing import Union, Tuple

import torch
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer

from square_model_inference.inference.model import Model
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput


class SentenceTransformer(Model):
    SUPPORTED_EMBEDDING_MODES = ["mean", "max", "cls", "token"]

    def __init__(self, model_name, max_batch_size, disable_gpu, **kwargs):
        self._load_model(model_name, disable_gpu)
        self.max_batch_size = max_batch_size

    def _load_model(self, model_name, disable_gpu):
        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.
        """
        logger.debug(f"Loading model {model_name}")
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = SentenceTransformer(model_name_or_path=model_name, device=device)
        logger.info(f"Model {model_name} loaded on {device}")
        self.model = model

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        embeddings = self.model.encode(request.input, batch_size=self.max_batch_size, show_progress_bar=False)
        return PredictionOutput(model_outputs={"embeddings": embeddings}, task_outputs={})


    async def predict(self, request: PredictionRequest) -> PredictionOutput:
        if request.is_preprocessed:
            ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")

        if request.task != Task.embedding:
            NotImplementedError("Only embedding task supported by this model")
        return self._embedding(request)

