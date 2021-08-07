import torch
from sentence_transformers import SentenceTransformer as SentenceTransformerModel

from square_model_inference.inference.model import Model
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput, PredictionOutputForEmbedding

import logging

logger = logging.getLogger(__name__)

class SentenceTransformer(Model):
    """
    The class for all sentence-transformers models
    """

    def __init__(self, model_name, batch_size, disable_gpu, max_input_size, **kwargs):
        """
        Initialize the SentenceTransformer
        :param model_name: the sentence-transformer model name (https://sbert.net/docs/pretrained_models.html)
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        :param max_input_size: requests with a larger input are rejected
        :param kwargs: Not used
        """
        self._load_model(model_name, disable_gpu)
        self.batch_size = batch_size
        self.max_input_size = max_input_size

    def _load_model(self, model_name, disable_gpu):
        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.
        """
        logger.debug(f"Loading model {model_name}")
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = SentenceTransformerModel(model_name_or_path=model_name, device=device)
        logger.info(f"Model {model_name} loaded on {device}")
        self.model = model

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        embeddings = self.model.encode(request.input, batch_size=self.batch_size, show_progress_bar=False)
        return PredictionOutputForEmbedding(model_outputs={"embeddings": embeddings})


    async def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")
        if len(request.input) > self.max_input_size:
            raise ValueError(f"Input is too large. Max input size is {self.max_input_size}")
        if task != Task.embedding:
            raise ValueError("Only embedding task supported by this model")
        return self._embedding(request)

