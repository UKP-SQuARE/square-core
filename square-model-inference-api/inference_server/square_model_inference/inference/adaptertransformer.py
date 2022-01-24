from transformers import AutoModelWithHeads, list_adapters

from square_model_inference.inference.transformer import Transformer
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput

import logging

logger = logging.getLogger(__name__)


class AdapterTransformer(Transformer):
    """
    The class for all adapter-based models using the adapter-transformers package
    """

    def __init__(self, model_name, batch_size, disable_gpu, transformers_cache, max_input_size, preloaded_adapters,
                 **kwargs):
        """

        Initialize the Adapter with its underlying Transformer and pre-load all available adapters from adapterhub.ml

        Args:
             model_name: the Huggingface model name
             batch_size: batch size used for inference
             disable_gpu: do not move model to GPU even if CUDA is available
             transformers_cache: Should be same as TRANSFORMERS_CACHE env variable. This folder will be used to store the adapters
             max_input_size: requests with a larger input are rejected
             kwargs: Not used
        """
        self._load_model(AutoModelWithHeads, model_name, disable_gpu)
        if preloaded_adapters:
            self._load_adapter(model_name, transformers_cache)
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_input_size = max_input_size

    def _load_adapter(self, model_name, transformers_cache):
        """
        Pre-load all available adapters for MODEL_NAME from adapterhub.ml.
        We parse the hub index to extract all names and then load each model.

        Args:
             model_name: the Huggingface model name
             transformers_cache: Should be same as TRANSFORMERS_CACHE env variable. This folder will be used to store the adapters

        """

        logger.info("Loading all available adapters")
        adapter_infos = []
        for source in ["ah", "hf"]:
            adapter_infos = [info for info in list_adapters(source=source) if info.model_name == model_name]
            if source == "ah":
                adapters = set(f"{adapter_info.task}/{adapter_info.subtask}@{adapter_info.username}" for adapter_info in
                               adapter_infos)
            elif source == "hf":
                adapters = set(f"{adapter_info.adapter_id}" for adapter_info in adapter_infos if
                               adapter_info.adapter_id.startswith("AdapterHub"))
            for adapter in adapters:
                logger.debug(f"Loading adapter {adapter}")
                try:
                    self.model.load_adapter(adapter, load_as=adapter, with_head=True, cache_dir=transformers_cache,
                                            source=source)
                except RuntimeError as e:
                    if "Error(s) in loading state_dict" in e.args[0]:
                        logger.debug(
                            f"Could not load {adapter} due to missing label_ids in config resulting in exception:\n{e.args[0]}")
                    else:
                        raise e
                except AttributeError as e:
                    if "Given head type " in e.args[0]:
                        logger.debug(f"Could not load {adapter} due to unknown head type:\n{e.args[0]}")
                    else:
                        raise e
        # Move all freshly loaded adapter weights to the same device as the model
        self.model.to(self.model.device)

    # def _load_single_adapter(self, adapter_name: str):
    #     if adapter_name not in self.model.config.adapters.adapters:
    #         logger.info(f"Loading new adapter {adapter_name}")
    #         self.model.load_adapter(adapter_name, with_head=True, load_as=adapter_name)
    #     else:
    #         logger.debug(f"Adapter {adapter_name} is already loaded. Not loading again")

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._token_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        return prediction

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        logger.info(f"sequence classification request:\n{request.json()}")
        prediction = super()._sequence_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        logger.info(f"sequence classification prediction:\n{prediction}")
        return prediction

    def _prepare_adapter(self, adapter_name):
        if adapter_name and adapter_name not in self.model.config.adapters.adapters:
            try:
                self.model.load_adapter(adapter_name, load_as=adapter_name)
            except EnvironmentError:
                self.model.load_adapter(adapter_name, load_as=adapter_name, source="hf")

        if not adapter_name or adapter_name not in self.model.config.adapters.adapters:
            raise ValueError(f"Unknown or missing adapter {adapter_name}. "
                             f"Please provider a fully specified adapter name from adapterhub.ml")
        self.model.set_active_adapters(adapter_name)

    async def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")
        if len(request.input) > self.max_input_size:
            raise ValueError(f"Input is too large. Max input size is {self.max_input_size}")
        self._prepare_adapter(request.adapter_name)

        if task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif task == Task.token_classification:
            return self._token_classification(request)
        elif task == Task.question_answering:
            return self._question_answering(request)
        elif task == Task.embedding:
            return self._embedding(request)
        elif task == Task.generation:
            return self._generation(request)
