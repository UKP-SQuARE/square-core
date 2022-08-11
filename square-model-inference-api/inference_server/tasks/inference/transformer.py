import logging
from collections import defaultdict
import string
from typing import Union, Tuple, List, Dict, Any

import numpy as np
import math
import torch
from torch.nn import Module, ModuleList
from tasks.config.model_config import model_config
from tasks.inference.model import Model

from tasks.attacks import hotflip, input_reduction, topk_tokens, subspan

from tasks.models.prediction import (
    PredictionOutput,
    PredictionOutputForSequenceClassification,
    PredictionOutputForTokenClassification,
    PredictionOutputForQuestionAnswering,
    PredictionOutputForGeneration,
    PredictionOutputForEmbedding,
)
from tasks.models.request import Task, PredictionRequest
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    AutoModelForCausalLM,
)
from transformers.models.gpt2.tokenization_gpt2 import bytes_to_unicode

logger = logging.getLogger(__name__)

CLASS_MAPPING = {
    "base": AutoModel,
    "sequence_classification": AutoModelForSequenceClassification,
    "token_classification": AutoModelForTokenClassification,
    "question_answering": AutoModelForQuestionAnswering,
    "generation": AutoModelForCausalLM,
}


class Transformer(Model):
    """
    The class for all Huggingface transformer-based models
    """

    SUPPORTED_EMBEDDING_MODES = ["mean", "max", "cls", "token", "pooler"]

    def __init__(self, **kwargs):
        """
        Initialize the Transformer
        Args:
             model_name: the Huggingface model name
             model_class: the class name (according to CLASS_MAPPING) to use
             disable_gpu: do not move model to GPU even if CUDA is available
             kwargs: Not used
        """
        if model_config.model_class == "from_config":
            config = AutoConfig.from_pretrained(model_config.model_name)
            model_arch = config.architectures[0]
            hf_modelling = model_arch.split("For")[-1]
            for task, hf_model in CLASS_MAPPING.items():
                if hf_modelling in hf_model.__name__:
                    model_cls = CLASS_MAPPING[task]
                    break
                else:
                    model_cls = CLASS_MAPPING["base"]
            CLASS_MAPPING["from_config"] = model_cls
        elif model_config.model_class not in CLASS_MAPPING:
            raise RuntimeError(
                f"Unknown MODEL_CLASS. Must be one of {CLASS_MAPPING.keys()}"
            )
        self._load_model(
            CLASS_MAPPING[model_config.model_class],
            model_config.model_name,
            model_config.disable_gpu,
        )

    def _load_model(self, model_cls, model_name, disable_gpu):

        """
        Load the Transformer model model_name and its tokenizer with Huggingface.
        Model will be moved to GPU unless CUDA is unavailable or disable_gpu is true.
        """

        logger.debug(f"Loading model {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() and not disable_gpu else "cpu"
        model = model_cls.from_pretrained(model_name).to(device)
        logger.info(f"Model {model_name} loaded on {device}")

        self.model = model
        self.tokenizer = tokenizer

    def encode(
        self, inputs: list = None, add_special_tokens: bool = True, return_tensors=None
    ):
        """
        Encode inputs using the model tokenizer
        Args:
            inputs: question, context pair as a list
            add_special_tokens: where to add CLS, SEP tokens
            return_tensors: whether to return tensors
        Return:
            tokenized inputs
        """
        return self.tokenizer(
            inputs,
            add_special_tokens=add_special_tokens,
            return_tensors=return_tensors,
            padding=True,
            truncation=True,
            max_length=512,
        )

    def decode(self, input_ids: torch.Tensor, skip_special_tokens: bool) -> List[str]:
        """
        Decode received input_ids into a list of word tokens.
        Args:
            input_ids (torch.Tensor): Input ids representing
            word tokens for a sentence/document.
        """
        return self.tokenizer.convert_ids_to_tokens(
            input_ids, skip_special_tokens=skip_special_tokens
        )

    def _ensure_tensor_on_device(self, **inputs):
        """
        Ensure PyTorch tensors are on the specified device.

        Args:
            inputs (keyword arguments that should be :obj:`torch.Tensor`):
                The tensors to place on :obj:`self.device`.

        Return:
            :obj:`Dict[str, torch.Tensor]`: The same as :obj:`inputs` but on the proper device.
        """
        return {name: tensor.to(self.model.device) for name, tensor in inputs.items()}

    def get_model_embeddings(
        self, embedding_type: str = "word_embeddings"
    ) -> Module or ModuleList:
        """
        Get the model embedding layer
        Args:
            embedding_type: can be one of word_embeddings,
                token_type_embeddings or position_embeddings
        """
        embeddings = Module or ModuleList
        model_prefix = self.model.base_model_prefix
        model_base = getattr(self.model, model_prefix)
        model_embeddings = getattr(model_base, "embeddings")
        if embedding_type == "word_embeddings":
            embeddings = model_embeddings.word_embeddings
        elif embedding_type == "token_type_embeddings":
            embeddings = model_embeddings.token_type_embeddings
        elif embedding_type == "position_embeddings":
            embeddings = model_embeddings.position_embeddings
        return embeddings

    def get_model_attentions(self) -> Module or ModuleList:
        """
        Get the model attention layer
        :return:
        """
        model_prefix = self.model.base_model_prefix
        model_base = getattr(self.model, model_prefix)
        model_enc = getattr(model_base, "encoder")
        # get attn weights from last layer
        attentions = model_enc.layer[-1].attention
        return attentions

    def _register_forward_hooks_attn(self, attentions_list: List):
        """
        Register the model attentions during the forward pass
        :param attentions_list:
        :return:
        """

        def forward_hook(module, inputs, output):
            attentions_list.append(
                output[1][:, :, 0, :].mean(1).squeeze(0).clone().detach()
            )

        handles = []
        attn_layer = self.get_model_attentions()
        handles.append(attn_layer.register_forward_hook(forward_hook))
        return handles

    def _register_hooks(self, embeddings_list: List, alpha: int, method: str):
        """
        Register the model embeddings during the forward pass
        Args:
            embeddings_list: list to store embeddings during forward pass
        """

        def forward_hook(module, inputs, output):
            if alpha == 0 and method in ["simple_grads", "integrated_grads"]:
                embeddings_list.append(output.squeeze(0).clone().detach())
            if method == "integrated_grads":
                # Scale the embedding by alpha
                output.mul_(alpha)
            elif method == "smooth_grads":
                torch.manual_seed(4)
                torch.cuda.manual_seed(4)
                # Random noise = N(0, stdev * (max-min))
                stdev = 0.01
                scale = output.detach().max() - output.detach().min()
                noise = torch.randn(output.shape, device=output.device) * stdev * scale

                # Add the random noise
                output.add_(noise)

        handles = []
        embedding_layer = self.get_model_embeddings()
        handles.append(embedding_layer.register_forward_hook(forward_hook))
        return handles

    def _register_embedding_gradient_hooks(self, embedding_grads: List):
        """
        Register the model gradients during the backward pass
        Args:
            embedding_grads: list to store the gradients
        """

        def hook_layers(module, grad_in, grad_out):
            grads = grad_out[0]
            embedding_grads.append(grads)

        hooks = []
        embedding_layer = self.get_model_embeddings()
        hooks.append(embedding_layer.register_full_backward_hook(hook_layers))
        return hooks

    def _register_attention_gradient_hooks(self, attn_grads: List):
        """
        Register the model gradients during the backward pass
        :param attn_grads:
        :return:
        """

        def hook_layers(module, grad_in, grad_out):
            grads = grad_out[0]
            attn_grads.append(grads)

        hooks = []
        attentions = self.get_model_attentions()
        hooks.append(attentions.register_full_backward_hook(hook_layers))
        return hooks

    def get_gradients(self, request: PredictionRequest, method: str, **kwargs):
        """
        Compute model gradients
        Args:
            inputs: list of question and context
            answer_start: answer span start
            answer_end: answer span end
        Return:
            dict of model gradients
        """

        original_param_name_to_requires_grad_dict = {}
        for param_name, param in self.model.named_parameters():
            original_param_name_to_requires_grad_dict[param_name] = param.requires_grad
            param.requires_grad = True

        gradients: List[torch.Tensor] = []
        if method == "scaled_attention":
            hooks: List = self._register_attention_gradient_hooks(gradients)
        else:
            hooks: List = self._register_embedding_gradient_hooks(gradients)
        with torch.backends.cudnn.flags(enabled=False):
            features = self.tokenizer(
                request.input, return_tensors="pt", **request.preprocessing_kwargs
            )
            input_features = self._ensure_tensor_on_device(**features)
            outputs = self.model(**input_features, **kwargs, **request.model_kwargs)
            loss = outputs.loss

            # Zero gradients.
            # NOTE: this is actually more efficient than
            # calling `self._model.zero_grad()`
            # because it avoids a read op when the
            # gradients are first updated below.
            for p in self.model.parameters():
                p.grad = None
            loss.backward()

        for hook in hooks:
            hook.remove()

        # if multiple entries, only choose emb grad for the correct answer
        if "labels" in kwargs.keys() and gradients[0].shape[0] > 1:
            gradients = [gradients[0][kwargs["labels"].item()].unsqueeze(0)]

        grad_dict = dict()
        for idx, grad in enumerate(gradients):
            key = "grad_input_" + str(idx + 1)
            grad_dict[key] = grad.detach().cpu().numpy()

        # restore the original requires_grad values of the parameters
        for param_name, param in self.model.named_parameters():
            param.requires_grad = original_param_name_to_requires_grad_dict[param_name]
        # print(grad_dict)
        return grad_dict

    def _predict(
        self, request: PredictionRequest, output_features=False
    ) -> Union[dict, Tuple[dict, dict]]:
        """
        Inference on the input.

        Args:
         request: the request with the input and optional kwargs
         output_features: return the features of the input.
            Necessary if, e.g., attention mask is needed for post-processing.

        Returns:
             The model outputs and optionally the input features
        """

        all_predictions = []
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get(
            "padding", True
        )
        request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get(
            "truncation", True
        )
        self.model.to(
            "cuda"
            if torch.cuda.is_available() and not model_config.disable_gpu
            else "cpu"
        )

        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        if request.explain_kwargs or request.attack_kwargs:
            self.decoded_texts = [
                self.decode(tokens, skip_special_tokens=False)
                for tokens in features["input_ids"]
            ]
            # remove padding tokens in MCQ
            self.num_pad_tokens = [
                text.count(self.tokenizer.pad_token) for text in self.decoded_texts
            ]
            self.decoded_texts = [
                list(filter(self.tokenizer.pad_token.__ne__, text))
                for text in self.decoded_texts
            ]
            self.word_mappings = [
                features.word_ids(i) for i in range(len(features["input_ids"]))
            ]

        if request.explain_kwargs:
            if request.explain_kwargs["method"] in ["attention", "scaled_attention"]:
                request.model_kwargs["output_attentions"] = True
        if request.attack_kwargs:
            if request.attack_kwargs["saliency_method"] in [
                "attention",
                "scaled_attention",
            ]:
                request.model_kwargs["output_attentions"] = True

        for start_idx in range(0, len(request.input), model_config.batch_size):
            with torch.no_grad():
                input_features = {
                    k: features[k][start_idx : start_idx + model_config.batch_size]
                    for k in features.keys()
                }
                input_features = self._ensure_tensor_on_device(**input_features)
                predictions = self.model(**input_features, **request.model_kwargs)
                all_predictions.append(predictions)

        keys = all_predictions[0].keys()
        final_prediction = {}
        for key in keys:
            # HuggingFace outputs for 'attentions' and more is
            # returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values'
            # which is only relevant for generation.
            # Generation should NOT use this function
            if isinstance(all_predictions[0][key], tuple):
                tuple_of_lists = list(
                    zip(
                        *[
                            [
                                torch.stack(p).cpu()
                                if isinstance(p, tuple)
                                else p.cpu()
                                for p in tpl[key]
                            ]
                            for tpl in all_predictions
                        ]
                    )
                )
                final_prediction[key] = tuple(torch.cat(l) for l in tuple_of_lists)
            else:
                final_prediction[key] = torch.cat(
                    [p[key].cpu() for p in all_predictions]
                )
        if output_features:
            return final_prediction, features

        return final_prediction

    def _interpret(
        self, request: PredictionRequest, prediction: Dict, method: str, **kwargs
    ):
        """
        gets the word attributions
        """

        embeddings_list: List[torch.Tensor] = []
        attentions_list: List[torch.Tensor] = []
        grads: Dict[str, Any] = {}
        instances_with_grads: Dict = {}

        if method == "simple_grads":
            # Hook used for saving embeddings
            handles: List = self._register_hooks(
                embeddings_list, alpha=0, method=method
            )
            try:
                grads = self.get_gradients(request, method, **kwargs)
            finally:
                for handle in handles:
                    handle.remove()

            if "labels" in kwargs.keys() and embeddings_list[0].shape[0] > 1:
                embeddings_list = [embeddings_list[0][kwargs["labels"].item()]]
            # Gradients come back in the reverse order that they
            # were sent into the network
            embeddings_list.reverse()
            embeddings_list = [
                embedding.cpu().detach().numpy() for embedding in embeddings_list
            ]

        elif method == "integrated_grads":
            # Use 10 terms in the summation approximation of the
            # integral in integrated grad
            steps = 10
            # Exclude the endpoint because we do a left point
            # integral approximation
            for alpha in np.linspace(0, 1.0, num=steps, endpoint=False):
                handles = []
                # Hook for modifying embedding value
                handles = self._register_hooks(embeddings_list, alpha, method=method)
                try:
                    gradients = self.get_gradients(request, method, **kwargs)
                finally:
                    for handle in handles:
                        handle.remove()

                # Running sum of gradients
                if grads == {}:
                    grads = gradients
                else:
                    for key in gradients.keys():
                        grads[key] += gradients[key]

            # Average of each gradient term
            for key in grads.keys():
                grads[key] /= steps

            if "labels" in kwargs.keys() and embeddings_list[0].shape[0] > 1:
                embeddings_list = [embeddings_list[0][kwargs["labels"].item()]]
            # Gradients come back in the reverse order that they
            # were sent into the network
            embeddings_list.reverse()
            embeddings_list = [
                embedding.cpu().detach().numpy() for embedding in embeddings_list
            ]
            # Element-wise multiply average gradient by the input
            for idx, input_embedding in enumerate(embeddings_list):
                key = "grad_input_" + str(idx + 1)
                grads[key] *= input_embedding

        elif method == "smooth_grads":
            num_samples = 10
            for _ in range(num_samples):
                handles = self._register_hooks(embeddings_list, alpha=0, method=method)
                try:
                    gradients = self.get_gradients(request, method, **kwargs)
                finally:
                    for handle in handles:
                        handle.remove()

                # Sum gradients
                if grads == {}:
                    grads = gradients
                else:
                    for key in gradients.keys():
                        grads[key] += gradients[key]

            # Average the gradients
            for key in grads.keys():
                grads[key] /= num_samples

        elif method == "attention":
            attn = prediction["attentions"][-1]
            weights = attn[:, :, 0, :].mean(1)
            # print("weights: ", weights.cpu().detach().numpy())
            # grads["grad_input_1"] = weights.cpu().detach().numpy()
            for value in range(len(weights)):
                input_key = "grad_input_" + str(value)
                # by grads we mean attributions here; for consistency
                grads[input_key] = weights.cpu().detach().numpy()[value]

        elif method == "scaled_attention":
            # Hook used for saving attentions
            handles: List = self._register_forward_hooks_attn(attentions_list)
            try:
                grads = self.get_gradients(request, method, **kwargs)
                # print(grads["grad_input_1"][:, :, 0, :].mean(1))
            finally:
                for handle in handles:
                    handle.remove()

            # Gradients come back in the reverse order that
            # they were sent into the network
            attentions_list.reverse()
            attentions_list = [attn.cpu().detach().numpy() for attn in attentions_list]

        emb_grad = np.array([])
        for key, grad in grads.items():
            # Get number at the end of every gradient key (they look like grad_input_[int],
            # we're getting this [int] part and subtracting 1 for zero-based indexing).
            # This is then used as an index into the reversed input array to match up the
            # gradient and its respective embedding.
            if method == "simple_grads":
                input_idx = int(key[-1]) - 1
                # The [0] here is undo-ing the batching that happens in get_gradients.
                emb_grad = np.sum(grad[0] * embeddings_list[input_idx][0], axis=1)
            elif method in ["integrated_grads", "smooth_grads"]:
                emb_grad = np.sum(grad[0], axis=1)
            elif method == "attention":
                # break
                emb_grad = grad
            elif method == "scaled_attention":
                input_idx = int(key[-1]) - 1
                emb_grad = np.sum(grad[0] * attentions_list[input_idx][0], axis=1)
            else:
                raise ValueError(
                    "Method not allowed. Please enter another explanation method."
                )
            norm = np.linalg.norm(emb_grad, ord=1)
            normalized_grad = [math.fabs(e) / norm for e in emb_grad]
            grads[key] = normalized_grad

        instances_with_grads["instance"] = grads
        attributions = list(instances_with_grads["instance"].values())
        return attributions

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        request.model_kwargs["output_hidden_states"] = True
        predictions, features = self._predict(request, output_features=True)
        # We remove hidden_states from predictions!
        if "hidden_states" in predictions:
            hidden_state = predictions.pop("hidden_states")[-1]
        elif "last_hidden_state" in predictions:
            hidden_state = predictions.get("last_hidden_state")
        elif "decoder_hidden_states" in predictions:
            hidden_state = predictions.get("decoder_hidden_states")[-1]
        else:
            raise ValueError(
                "No hidden state available in keys: {}".format(predictions.keys())
            )
        attention_mask = features["attention_mask"]

        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        task_outputs = {"embedding_mode": embedding_mode}

        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list "
                f"of supported modes {self.SUPPORTED_EMBEDDING_MODES}"
            )

        if embedding_mode == "cls":
            emb = hidden_state[:, 0, :]
        elif embedding_mode == "pooler":
            emb = predictions["pooler_output"]
        # copied from sentence-transformers pooling
        elif embedding_mode == "max":
            input_mask_expanded = (
                attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            )
            hidden_state[
                input_mask_expanded == 0
            ] = -1e9  # Set padding tokens to large negative value
            emb = torch.max(hidden_state, 1)[0]
        # copied from sentence-transformers pooling
        elif embedding_mode == "mean":
            input_mask_expanded = (
                attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            )
            sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
            sum_mask = input_mask_expanded.sum(1)
            emb = sum_embeddings / sum_mask
        elif embedding_mode == "token":
            emb = hidden_state
            task_outputs["word_ids"] = [
                features.word_ids(i) for i in range(len(request.input))
            ]
        predictions["embeddings"] = emb
        return PredictionOutputForEmbedding(model_outputs=predictions, **task_outputs)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        label2id = self.model.config.label2id
        id2label = {v: k for k, v in label2id.items()}
        task_outputs = {
            "id2label": id2label,
            "word_ids": [features.word_ids(i) for i in range(len(request.input))],
        }
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get(
            "is_regression", False
        ):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(
                predictions["logits"], dim=-1
            ).tolist()

        return PredictionOutputForTokenClassification(
            model_outputs=predictions, **task_outputs
        )

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions = self._predict(request)
        label2id = self.model.config.label2id
        id2label = {v: k for k, v in label2id.items()}
        task_outputs = {"id2label": id2label, "attributions": []}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get(
            "is_regression", False
        ):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            labels = torch.argmax(predictions["logits"], dim=-1)
            task_outputs["labels"] = labels.tolist()

        # word attributions
        if request.explain_kwargs:
            grad_kwargs = {"labels": labels.to(self.model.device)}
            attributions = self._interpret(
                request=request,
                prediction=predictions,
                method=request.explain_kwargs["method"],
                **grad_kwargs,
            )
            predictions.pop("attentions", None)
            word_imp = self.process_outputs(
                attributions=attributions,
                top_k=request.explain_kwargs["top_k"],
                mode=request.explain_kwargs["mode"],
                task="sequence_classification",
            )
            task_outputs["attributions"] = word_imp

        return PredictionOutputForSequenceClassification(
            model_outputs=predictions, **task_outputs
        )

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get(
            "padding", False
        )
        request.preprocessing_kwargs[
            "add_special_tokens"
        ] = request.preprocessing_kwargs.get("add_special_tokens", False)
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)

        # We cannot batch generate, so we have to do it separately for each input prompt.
        for prompt in request.input:
            features = self.tokenizer(
                prompt, return_tensors="pt", **request.preprocessing_kwargs
            )
            input_ids = features["input_ids"]
            input_ids = self._ensure_tensor_on_device(input_ids=input_ids)["input_ids"]
            request.model_kwargs.update(request.task_kwargs)
            request.model_kwargs["return_dict_in_generate"] = True
            res = self.model.generate(input_ids, **request.model_kwargs)

            # put everything on CPU and add it to model_outputs
            for key in res.keys():
                if isinstance(res[key], tuple):
                    if isinstance(res[key][0], tuple):
                        res[key] = tuple(
                            (tuple(tensor.cpu() for tensor in tpl)) for tpl in res[key]
                        )
                    else:
                        res[key] = tuple(tensor.cpu() for tensor in res[key])
                else:
                    res[key] = res[key].cpu()
                model_outputs[key].append(res[key])

            generated_texts = [
                self.tokenizer.decode(
                    seq,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=request.task_kwargs.get(
                        "clean_up_tokenization_spaces", False
                    ),
                )
                for seq in res["sequences"]
            ]
            task_outputs["generated_texts"].append(generated_texts)
        return PredictionOutputForGeneration(
            model_outputs=model_outputs, **task_outputs
        )

    def _question_answering(self, request: PredictionRequest) -> PredictionOutput:
        """
        Span-based question answering for a given question and context.
        We expect the input to use the (question, context) format for the text pairs.

        Args:
          request: the prediction request

        """
        # Making heavy use of https://huggingface.co/transformers/
        # _modules/transformers/pipelines/question_answering.html#QuestionAnsweringPipeline
        def decode(
            start_: np.ndarray,
            end_: np.ndarray,
            topk: int,
            max_answer_len: int,
            undesired_tokens_: np.ndarray,
        ) -> Tuple:
            """
            Take the output of any :obj:`ModelForQuestionAnswering` and
                will generate probabilities for each span to be the
                actual answer.

            In addition, it filters out some unwanted/impossible cases
            like answer len being greater than max_answer_len or
            answer end position being before the starting position.
            The method supports output the k-best answer through
            the topk argument.

            Args:
                start_ (:obj:`np.ndarray`): Individual start
                    probabilities for each token.
                end (:obj:`np.ndarray`): Individual end_ probabilities
                    for each token.
                topk (:obj:`int`): Indicates how many possible answer
                    span(s) to extract from the model output.
                max_answer_len (:obj:`int`): Maximum size of the answer
                    to extract from the model's output.
                undesired_tokens_ (:obj:`np.ndarray`): Mask determining
                    tokens that can be part of the answer
            """
            # Ensure we have batch axis
            if start_.ndim == 1:
                start_ = start_[None]

            if end_.ndim == 1:
                end_ = end_[None]

            # Compute the score of each tuple(start_, end_) to be the real answer
            outer = np.matmul(np.expand_dims(start_, -1), np.expand_dims(end_, 1))

            # Remove candidate with end_ < start_ and end_ - start_ > max_answer_len
            candidates = np.tril(np.triu(outer), max_answer_len - 1)

            #  Inspired by Chen & al. (https://github.com/facebookresearch/DrQA)
            scores_flat = candidates.flatten()
            if topk == 1:
                idx_sort = [np.argmax(scores_flat)]
            elif len(scores_flat) < topk:
                idx_sort = np.argsort(-scores_flat)
            else:
                idx = np.argpartition(-scores_flat, topk)[0:topk]
                idx_sort = idx[np.argsort(-scores_flat[idx])]

            starts_, ends_ = np.unravel_index(idx_sort, candidates.shape)[1:]
            desired_spans = np.isin(starts_, undesired_tokens_.nonzero()) & np.isin(
                ends_, undesired_tokens_.nonzero()
            )
            starts_ = starts_[desired_spans]
            ends_ = ends_[desired_spans]
            scores_ = candidates[0, starts_, ends_]

            return starts_, ends_, scores_

        request.preprocessing_kwargs["truncation"] = "only_second"
        predictions, features = self._predict(request, output_features=True)

        task_outputs = {
            "answers": [],
            "attributions": [],
            "adversarial": {"indices": [],},  # for hotflip, input_reduction and topk
        }
        for idx, (start, end, (_, context)) in enumerate(
            zip(predictions["start_logits"], predictions["end_logits"], request.input)
        ):
            start = start.numpy()
            end = end.numpy()
            # Ensure padded tokens & question tokens cannot
            # belong to the set of candidate answers.
            question_tokens = np.abs(
                np.array([s != 1 for s in features.sequence_ids(idx)]) - 1
            )
            # Unmask CLS token for 'no answer'
            question_tokens[0] = 1
            undesired_tokens = question_tokens & features["attention_mask"][idx].numpy()

            # Generate mask
            undesired_tokens_mask = undesired_tokens == 0.0

            # Make sure non-context indexes in the tensor cannot
            # contribute to the softmax
            start = np.where(undesired_tokens_mask, -10000.0, start)
            end = np.where(undesired_tokens_mask, -10000.0, end)

            start = np.exp(
                start - np.log(np.sum(np.exp(start), axis=-1, keepdims=True))
            )
            end = np.exp(end - np.log(np.sum(np.exp(end), axis=-1, keepdims=True)))

            # Get score for 'no answer' then mask for decoding step (CLS token
            no_answer_score = (start[0] * end[0]).item()
            start[0] = end[0] = 0.0

            starts, ends, scores = decode(
                start,
                end,
                request.task_kwargs.get("topk", 1),
                request.task_kwargs.get("max_answer_len", 128),
                undesired_tokens,
            )
            enc = features[idx]
            self.original_ans_start = enc.token_to_word(starts[0])
            self.original_ans_end = enc.token_to_word(ends[0])
            answers = [
                {
                    "score": score.item(),
                    "start": enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[
                        0
                    ],
                    "end": enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1],
                    "answer": context[
                        enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[
                            0
                        ] : enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1]
                    ],
                }
                for s, e, score in zip(starts, ends, scores)
            ]
            if request.task_kwargs.get("show_null_answers", True):
                answers.append(
                    {"score": no_answer_score, "start": 0, "end": 0, "answer": ""}
                )
            answers = sorted(answers, key=lambda x: x["score"], reverse=True)[
                : request.task_kwargs.get("topk", 1)
            ]
            task_outputs["answers"].append(answers)

            # word attributions
            if request.explain_kwargs or request.attack_kwargs:
                # attributions = []
                # if request.explain_kwargs["method"] == "attention":
                #     attn = predictions["attentions"][-1]
                #     weights = attn[:, :, 0, :].mean(1)
                #     attributions = weights.cpu().detach().numpy()[0]
                # else:
                start_idx = torch.argmax(predictions["start_logits"])
                end_idx = torch.argmax(predictions["end_logits"])
                answer_start = torch.tensor([start_idx])
                answer_end = torch.tensor([end_idx])

                grad_kwargs = {
                    "start_positions": answer_start.to(self.model.device),
                    "end_positions": answer_end.to(self.model.device),
                }
                attributions = self._interpret(
                    request=request,
                    prediction=predictions,
                    method=request.explain_kwargs["method"]
                    if request.explain_kwargs
                    else request.attack_kwargs["saliency_method"],
                    **grad_kwargs,
                )

                word_imp = self.process_outputs(
                    attributions=attributions,
                    top_k=request.explain_kwargs["top_k"]
                    if request.explain_kwargs
                    else 10,
                    mode=request.explain_kwargs["mode"]
                    if request.explain_kwargs
                    else "all",
                    task="question_answering",
                )
                task_outputs["attributions"] = word_imp

            if (
                not request.attack_kwargs
                and not request.explain_kwargs
                and not request.model_kwargs.get("output_attentions", False)
            ):
                predictions.pop("attentions", None)

            if request.attack_kwargs:
                new_predictions = self._model_attacks(request, task_outputs)
                return new_predictions

        return PredictionOutputForQuestionAnswering(
            model_outputs=predictions, **task_outputs
        )

    def _model_attacks(self, request, task_outputs):
        if request.attack_kwargs["method"] == "hotflip":
            attack = hotflip.Hotflip(
                tokenizer=self.tokenizer,
                top_k=request.attack_kwargs.get("max_flips", 10),
                include_answer=request.attack_kwargs.get("include_answer", False),
            )
            inputs, indices = attack.flip_tokens(
                task_outputs,
                ans_start=self.original_ans_start,
                ans_end=self.original_ans_end,
            )

            prediction_request = {
                "input": inputs,
                "is_preprocessed": False,
                "preprocessing_kwargs": {},
                "model_kwargs": {},
                "task_kwargs": {},
            }
            predictions = self._question_answering(
                PredictionRequest(**prediction_request)
            )
            predictions.contexts = [inp[1] for inp in inputs]
            predictions.adversarial["indices"] = indices

        elif request.attack_kwargs["method"] == "input_reduction":
            top_k = request.attack_kwargs.get("max_reductions", 10)
            attack = input_reduction.InputReduction(top_k=top_k,)
            inputs, indices = attack.reduce_instance(task_outputs)
            prediction_request = {
                "input": inputs,
                "is_preprocessed": False,
                "preprocessing_kwargs": {},
                "model_kwargs": {"output_attentions": True},
                "task_kwargs": {},
                "explain_kwargs": {
                    "method": "attention",
                    "top_k": top_k,
                    "mode": "all",
                },
            }
            predictions = self._question_answering(
                PredictionRequest(**prediction_request)
            )
            predictions.model_outputs.pop("attentions", None)
            predictions.questions = [inp[0] for inp in inputs]
            predictions.adversarial["indices"] = indices

        elif request.attack_kwargs["method"] is "topk_tokens" or "sub_span":
            top_k = request.attack_kwargs.get("max_tokens", 10)

            if request.attack_kwargs["method"] == "topk_tokens":
                attack = topk_tokens.TopkTokens(top_k=top_k,)
                inputs, indices = attack.choose_topk(task_outputs)
            elif request.attack_kwargs["method"] == "sub_span":
                attack = subspan.SubSpan(top_k=top_k,)
                inputs, indices = attack.select_span(task_outputs)

            prediction_request = {
                "input": inputs,
                "is_preprocessed": False,
                "preprocessing_kwargs": {},
                "model_kwargs": {"output_attentions": True},
                "task_kwargs": {},
            }
            predictions = self._question_answering(
                PredictionRequest(**prediction_request)
            )
            predictions.model_outputs.pop("attentions", None)
            predictions.contexts = [inp[1] for inp in inputs]
            predictions.adversarial["indices"] = indices

        return predictions

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        """
        The selector prediction function that calls the
        main prediction function according to the task
        """
        if request.is_preprocessed:
            raise ValueError(
                "is_preprocessed=True is not "
                "supported for this model. "
                "Please use text as input."
            )
        if len(request.input) > model_config.max_input_size:
            raise ValueError(
                f"Input is too large. Max input size is "
                f"{model_config.max_input_size}"
            )

        if task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif task == Task.token_classification:
            return self._token_classification(request)
        elif task == Task.embedding:
            return self._embedding(request)
        elif task == Task.question_answering:
            return self._question_answering(request)
        elif task == Task.generation:
            return self._generation(request)

    def _bpe_decode(
        self, tokens: List[str], attributions: List
    ) -> Tuple[List[str], np.array]:
        """
        Byte-pair encoding for roberta-type models
        Merges sub-words to actual words
        """

        byte_encoder = bytes_to_unicode()
        byte_decoder = {v: k for k, v in byte_encoder.items()}
        decoded_each_tok = [
            bytearray([byte_decoder[c] for c in t.replace(" ", "Ġ")]).decode(
                encoding="utf-8", errors="replace"
            )
            for t in tokens
        ]

        end_points = []
        force_break = False
        for idx, token in enumerate(decoded_each_tok):
            # special token, punctuation, alphanumeric
            if (
                token in self.tokenizer.all_special_tokens
                or token in string.punctuation
                or not any([x.isalnum() for x in token.lstrip()])
                or token.lstrip == "'s"
            ):
                end_points.append(idx)
                force_break = True
                continue

            if force_break:
                end_points.append(idx)
                force_break = False
                continue

            if token[0] == " ":
                tokens[idx] = token[:]
                end_points.append(idx)

        end_points.append(len(tokens))

        segments = []
        for i in range(1, len(end_points)):
            if end_points[i - 1] == end_points[i]:
                continue
            segments.append((end_points[i - 1], end_points[i]))

        filtered_tokens, scores = [], []
        for s0, s1 in segments:
            filtered_tokens.append("".join(decoded_each_tok[s0:s1]))
            scores.append(np.sum(attributions[s0:s1], axis=0))
        filtered_tokens = [token.lstrip() for token in filtered_tokens]
        attribution_score = np.stack(scores, axis=0)

        return filtered_tokens, attribution_score

    def _wordpiece_decode(
        self, tokens: List[str], attributions: List, word_map: List
    ) -> Tuple[List[str], np.array]:

        """
        Wordpiece encoding for bert-type models
        Merges sub-words to actual words
        """

        decoded_each_tok = tokens
        chars_to_handle = ["s", "t", "ve", "re", "m", "n't"]

        context_start = tokens.index(self.tokenizer.sep_token)
        for idx, token in enumerate(decoded_each_tok[:-1]):
            if (
                token not in self.tokenizer.all_special_tokens
                and token == "'"
                and decoded_each_tok[idx + 1] in chars_to_handle
                and idx < context_start
            ):
                word_map[idx] = word_map[idx - 1]
                word_map[idx + 1] = word_map[idx - 1]
                word_map[idx + 2 : context_start] = [
                    w - 2 for w in word_map[idx + 2 : context_start] if w
                ]
                continue
            if (
                token not in self.tokenizer.all_special_tokens
                and token == "'"
                and decoded_each_tok[idx + 1] in chars_to_handle
                and idx > context_start
            ):
                word_map[idx] = word_map[idx - 1]
                word_map[idx + 1] = word_map[idx - 1]
                word_map[idx + 2 : -1] = [w - 2 for w in word_map[idx + 2 : -1] if w]
                continue

        filtered_tokens = [decoded_each_tok[0]]
        for idx, (word_idx, word) in enumerate(zip(word_map, decoded_each_tok[1:])):
            if word_idx == word_map[idx + 1] and not word == self.tokenizer.sep_token:
                filtered_tokens[-1] = f'{filtered_tokens[-1]}{word.replace("##", "")}'
            else:
                filtered_tokens.append(word)

        attribution_score = [attributions[0]]
        for idx, (word_idx, score) in enumerate(zip(word_map, attributions[1:])):
            if word_idx == word_map[idx + 1] and word_idx is not None:
                attribution_score[-1] = attribution_score[-1] + score
            else:
                attribution_score.append(score)

        return filtered_tokens, np.array(attribution_score)

    def process_outputs(
        self, attributions: List[List], top_k: int, mode: str, task: str
    ) -> List[Dict]:
        """
        post-process the word attributions to merge the sub-words tokens
        to words
        Args:
            attributions: word importance scores
            top_k: number of top word attributions
            mode: whether to show attribution in question, context or both
        Returns:
            dict of processed words along with their scores
        """

        question_indices, context_indices, question_tokens, context_tokens = (
            [],
            [],
            [],
            [],
        )
        dec_texts = self.decoded_texts

        for idx, score in enumerate(attributions):
            filtered_tokens: list = []
            importance: np.array = np.array([])
            sep_tokens: int = 0
            if self.model.config.model_type in ["roberta", "bart"]:
                filtered_tokens, importance = self._bpe_decode(dec_texts[idx], score)
                sep_tokens = 2
            elif self.model.config.model_type == "bert":
                filtered_tokens, importance = self._wordpiece_decode(
                    dec_texts[idx], score, word_map=self.word_mappings[idx]
                )
                importance = importance[: -self.num_pad_tokens[idx] or None]
                sep_tokens = 1

            result = [(w, a) for w, a in zip(filtered_tokens, importance) if w != ""]
            assert len(filtered_tokens) == len(
                importance
            ), "filtered tokens do not equal attributions"
            # outputs = {"attributions": result}
            context_start = filtered_tokens.index(self.tokenizer.sep_token)
            # account for cls token in result
            question = [
                (idx, v[0], v[1])
                for idx, v in enumerate(result[1:])
                if idx < context_start - 1
            ]

            context = [
                (idx - len(question) - sep_tokens, v[0], v[1])
                for idx, v in enumerate(result[1:])
                if idx > context_start - 1 and v[0] != self.tokenizer.sep_token
            ]

            if task == "sequence_classification":
                # adapter models for MCQ on square
                # use the [context, query] format
                # a format that is opposite to other models
                tmp = question
                question = context
                context = tmp
                # remove answer choice in MCQ
                # currently the answer choice can only be found via ?
                # TODO: improve this later
                question_mark_idx = [sym[0] for sym in question if "?" in sym]
                question = (
                    [q for i, q in enumerate(question) if i <= question_mark_idx[0]]
                    if question_mark_idx
                    else question
                )

            outputs, outputs_question, outputs_context = [], [], []
            if mode == "question" or mode == "all":
                outputs_question = [
                    i
                    for i, k, v in sorted(
                        question, key=lambda item: item[2], reverse=True
                    )[:top_k]
                ]
            if mode == "context" or mode == "all":
                outputs_context = [
                    i
                    for i, k, v in sorted(
                        context, key=lambda item: item[2], reverse=True
                    )[:top_k]
                ]

            # normalize values
            question_scores = [
                np.round(float(v) / sum(importance), 3) for _, _, v in question
            ]
            context_scores = [
                np.round(float(v) / sum(importance), 3) for _, _, v in context
            ]
            question = [
                (ques[0], ques[1], float(score))
                for ques, score in zip(question, question_scores)
            ]
            context = [
                (cxt[0], cxt[1], float(score))
                for cxt, score in zip(context, context_scores)
            ]

            question_tokens.append(question)
            context_tokens.append(context)
            question_indices.append(outputs_question)
            context_indices.append(outputs_context)

        outputs = [
            {
                "topk_question_idx": question_indices,
                "topk_context_idx": context_indices,
                "question_tokens": question_tokens,
                "context_tokens": context_tokens,
            }
        ]
        return outputs
