from typing import Callable

from fastapi import FastAPI

from square_model_inference.inference.adaptertransformer import AdapterTransformer
from square_model_inference.core.config import model_config
from square_model_inference.inference.sentencetransformer import SentenceTransformer
from square_model_inference.inference.transformer import Transformer
from square_model_inference.inference.onnx import Onnx

import logging

logger = logging.getLogger(__name__)

MODEL_MAPPING = {
    "adapter": AdapterTransformer,
    "transformer": Transformer,
    "sentence-transformer": SentenceTransformer,
    "onnx": Onnx,
}


def _startup_model(app: FastAPI) -> None:
    """
    Initialize the model used by the server and set it to the app state for global access
    """
    if model_config.model_type not in MODEL_MAPPING:
        raise RuntimeError(f"Unknown MODEL_MAPPING. Must be one of {MODEL_MAPPING.keys()}")

    model_instance = MODEL_MAPPING[model_config.model_type]()
    app.state.model = model_instance


def _shutdown_model(app: FastAPI) -> None:
    app.state.model = None


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model(app)

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)

    return shutdown
