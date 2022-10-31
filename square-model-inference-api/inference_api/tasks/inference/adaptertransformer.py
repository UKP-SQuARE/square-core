import logging
import os

from tasks.config.model_config import model_config
from tasks.models.prediction import PredictionOutput
from tasks.models.request import PredictionRequest, Task
from transformers.adapters import AutoAdapterModel, list_adapters
from transformers.adapters.heads import CausalLMHead

from .transformer import Transformer

logger = logging.getLogger(__name__)


class AdapterTransformer(Transformer):
    """
    The class for all adapter-based models using the adapter-transformers package
    """

    def __init__(self, **kwargs):
        """
        Initialize the Adapter with its underlying Transformer 
        and pre-load all available adapters from adapterhub.ml

        Args:
             model_name: the Huggingface model name
             disable_gpu: do not move model to GPU even if CUDA is available
             transformers_cache: Should be same as TRANSFORMERS_CACHE 
                env variable. This folder will be used to store the adapters
             kwargs: Not used
        """
        self.task = None
        self.gradients = None
        self._load_model(
            AutoAdapterModel, model_config.model_name, model_config.disable_gpu
        )
        if model_config.preloaded_adapters:
            self._load_adapter(model_config.model_name, model_config.transformers_cache)
        self.model_name = model_config.model_name

    def _load_adapter(self, model_name, transformers_cache):
        """
        Pre-load all available adapters for MODEL_NAME from adapterhub.ml.
        We parse the hub index to extract all names and then load each model.

        Args:
             model_name: the Huggingface model name
             transformers_cache: Should be same as TRANSFORMERS_CACHE env variable.
                This folder will be used to store the adapters

        """

        logger.info("Loading all available adapters")
        adapter_infos = []
        for source in ["ah", "hf"]:
            adapter_infos = [
                info
                for info in list_adapters(source=source)
                if info.model_name == model_name
            ]
            if source == "ah":
                adapters = set(
                    f"{adapter_info.task}/{adapter_info.subtask}@{adapter_info.username}"
                    for adapter_info in adapter_infos
                )
            elif source == "hf":
                adapters = set(
                    f"{adapter_info.adapter_id}"
                    for adapter_info in adapter_infos
                    if adapter_info.adapter_id.startswith("AdapterHub")
                )
            for adapter in adapters:
                logger.debug(f"Loading adapter {adapter}")
                try:
                    self.model.load_adapter(
                        adapter,
                        load_as=adapter,
                        with_head=True,
                        cache_dir=transformers_cache,
                        source=source,
                    )
                except RuntimeError as e:
                    if "Error(s) in loading state_dict" in e.args[0]:
                        logger.debug(
                            f"Could not load {adapter} due to missing label_ids in "
                            f"config resulting in exception:\n{e.args[0]}"
                        )
                    else:
                        raise e
                except AttributeError as e:
                    if "Given head type " in e.args[0]:
                        logger.debug(
                            f"Could not load {adapter} due to unknown head type:\n{e.args[0]}"
                        )
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
        # We only have to change the label2id mapping from config.label2id
        # (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._token_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        return prediction

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from
        # config.label2id (what super() uses) to the mapping
        # of the chosen head
        logger.info(f"sequence classification request:\n{request.json()}")
        self.model.config.prediction_heads[request.adapter_name]["num_choices"] = len(
            request.input
        )
        logger.info(
            f"num_choices: {self.model.config.prediction_heads[request.adapter_name]['num_choices']}"
        )
        prediction = super()._sequence_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v: k for k, v in label2id.items()}
        prediction.id2label = id2label

        logger.info(f"sequence classification prediction:\n{prediction.labels}")
        return prediction

    def _prepare_adapter(self, adapter_name):
        if adapter_name is not None:
            TEST = os.environ.get("TEST", "0")
            if TEST == "1":
                self.model.load_adapter(
                    adapter_name,
                    model_name="bert-base-uncased",
                    load_as=adapter_name,
                    source=None,
                )
            if TEST == "0":
                self.model.load_adapter(adapter_name, load_as=adapter_name, source=None)

        if not adapter_name or adapter_name not in self.model.config.adapters.adapters:
            raise ValueError(
                f"Unknown or missing adapter {adapter_name}. "
                f"Please provider a fully specified adapter name from adapterhub.ml"
            )
        self.model.set_active_adapters(adapter_name)

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        # ensure that the loaded had is a lm head
        if self.model.active_head is None or not isinstance(
            self.model.active_head, CausalLMHead
        ):
            # if there is no head or a head that is not a lm head add a lm head
            # depending on the model class different heads might be available
            # e.g. GPT2 -> causal lm head, BART -> seq2seq lm head
            if hasattr(self.model, "add_causal_lm_head"):
                self.model.add_causal_lm_head("lm_head", True)
            elif hasattr(self.model, "add_seq2seq_lm_head"):
                self.model.add_seq2seq_lm_head("lm_head", True)
        return super()._generation(request)

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError(
                "is_preprocessed=True is not supported for this model. Please use text as input."
            )
        if len(request.input) > model_config.max_input_size:
            raise ValueError(
                f"Input is too large. Max input size is {model_config.max_input_size}"
            )
        self._prepare_adapter(request.adapter_name)

        self.task = task
        if self.task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif self.task == Task.token_classification:
            return self._token_classification(request)
        elif self.task == Task.question_answering:
            return self._question_answering(request)
        elif self.task == Task.embedding:
            return self._embedding(request)
        elif self.task == Task.generation:
            return self._generation(request)
