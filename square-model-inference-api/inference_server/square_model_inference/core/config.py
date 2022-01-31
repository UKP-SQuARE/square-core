from dataclasses import dataclass, asdict
from collections.abc import Mapping
from square_model_inference.models.statistics import ModelStatistics

from starlette.config import Config

APP_VERSION = "0.1.0"
APP_NAME = "SQuARE Model Inference API"
API_PREFIX = "/api"

@dataclass
class ModelConfig(Mapping):
    # Corresponds to the Huggingface name for finetuned Transformers or the name of a finetuned SentenceTransformers
    model_name: str = None
    # Type of the model, e.g. Transformers, Adapter, ...
    # See square_model_inference.core.event_handlers.MODEL_MAPPING for all available names with corresponding model
    model_type: str = None

    # Path to the onnx file of the model (this is necessary for onnx models)
    model_path: str = None
    decoder_path: str = None

    preloaded_adapters: bool = True
    # Disable CUDA even if available
    disable_gpu: bool = False
    # Batch size used for many inputs
    batch_size: int = 32
    # Inputs larger than this size are rejected
    max_input_size: int = 1024

    # Cache directory where model weights are stored
    # This is the name for the env variable used by transformers and sentence-transformers package
    transformers_cache: str = None

    # For MODEL_TYPE=transformers: decides the AutoModel* class used
    # See square_model_inference.inference.transformer.CLASS_MAPPING for valid names and corresponding class
    model_class: str = "base"

    # Flag that decides if returned numpy arrays are returned
    # as lists or encoded to base64 (smaller but not easily human readable).
    # See the comment in square_model_inference.models.prediction._encode_numpy on information on how to decode
    # the base64 string back to the numpy array
    return_plaintext_arrays: bool = False

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def to_dict(self):
        return asdict(self)

    def to_statistics(self):
        return ModelStatistics(
            model_type=self.model_type,
            model_name=self.model_name,
            model_class=self.model_class,
            batch_size=self.batch_size,
            max_input=self.max_input_size,
            disable_gpu=self.disable_gpu,
            return_plaintext_arrays=self.return_plaintext_arrays,
        )

    @staticmethod
    def load(path=".env"):
        config = Config(path)
        return ModelConfig(
            model_name=config("MODEL_NAME", default=None),
            model_type=config("MODEL_TYPE", default=None),
            model_path=config("MODEL_PATH", default=None),
            decoder_path=config("DECODER_PATH", default=None),
            preloaded_adapters=config("PRELOADED_ADAPTERS", cast=bool, default=True),
            disable_gpu=config("DISABLE_GPU", cast=bool, default=False),
            batch_size=config("BATCH_SIZE", cast=int, default=32),
            max_input_size=config("MAX_INPUT_SIZE", cast=int, default=1024),
            transformers_cache=config("TRANSFORMERS_CACHE", default=None),
            model_class=config("MODEL_CLASS", default="base"),
            return_plaintext_arrays=config("RETURN_PLAINTEXT_ARRAYS", cast=bool, default=False),
            )


model_config = ModelConfig.load()


# for testing the inference models
def set_test_config(model_name, disable_gpu, batch_size, max_input_size, model_class="base", cache="./.cache", preloaded_adapters=False, onnx_path="", decoder_path=""):
    global model_config
    model_config.model_name = model_name
    model_config.model_class = model_class
    model_config.disable_gpu = disable_gpu
    model_config.batch_size = batch_size
    model_config.max_input_size = max_input_size
    model_config.transformers_cache = cache
    model_config.preloaded_adapters = preloaded_adapters
    model_config.model_path = onnx_path
    model_config.decoder_path = decoder_path
