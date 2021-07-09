import json
from collections import defaultdict
from typing import Union, Tuple

import torch
from loguru import logger
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, \
    AutoModelForTokenClassification, AutoModelForQuestionAnswering, AutoModelForCausalLM

from square_model_inference.inference.model import Model
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput, PredictionOutputForSequenceClassification, PredictionOutputForTokenClassification, \
    PredictionOutputForQuestionAnswering, PredictionOutputForGeneration, PredictionOutputForEmbedding

CLASS_MAPPING = {
    "base": AutoModel,
    "sequence_classification": AutoModelForSequenceClassification,
    "token_classification": AutoModelForTokenClassification,
    "question_answering": AutoModelForQuestionAnswering,
    "generation": AutoModelForCausalLM
}

class Transformer(Model):
    """
    The class for all Huggingface transformer-based models
    """
    SUPPORTED_EMBEDDING_MODES = ["mean", "max", "cls", "token"]

    def __init__(self, model_name, model_class, batch_size, disable_gpu, max_input_size, **kwargs):
        """
        Initialize the Transformer
        :param model_name: the Huggingface model name
        :param model_class: the class name (according to CLASS_MAPPING) to use
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        :param max_input_size: requests with a larger input are rejected
        :param kwargs: Not used
        """
        if model_class not in CLASS_MAPPING:
            raise RuntimeError(f"Unknown MODEL_CLASS. Must be one of {CLASS_MAPPING.keys()}")
        self._load_model(CLASS_MAPPING[model_class], model_name, disable_gpu)
        self.batch_size = batch_size
        self.max_input_size = max_input_size

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

    def _ensure_tensor_on_device(self, **inputs):
        """
        Ensure PyTorch tensors are on the specified device.

        Args:
            inputs (keyword arguments that should be :obj:`torch.Tensor`): The tensors to place on :obj:`self.device`.

        Return:
            :obj:`Dict[str, torch.Tensor]`: The same as :obj:`inputs` but on the proper device.
        """
        return {name: tensor.to(self.model.device) for name, tensor in inputs.items()}

    def _predict(self, request: PredictionRequest, output_features=False) \
            -> Union[dict, Tuple[dict, dict]]:
        """
        Inference on the input.
        :param request: the request with the input and optional kwargs
        :param output_features: return the features of the input.
        Necessary if, e.g., attention mask is needed for post-processing.
        :return: The model outputs and optionally the input features
        """
        all_predictions = []
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get("padding", True)
        request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get("truncation", True)
        features = self.tokenizer(request.input,
                                  return_tensors="pt",
                                  **request.preprocessing_kwargs)
        for start_idx in range(0, len(request.input), self.batch_size):
            with torch.no_grad():
                input_features = {k: features[k][start_idx:start_idx+self.batch_size] for k in features.keys()}
                input_features = self._ensure_tensor_on_device(**input_features)
                predictions = self.model(**input_features, **request.model_kwargs)
                all_predictions.append(predictions)
        keys = all_predictions[0].keys()
        final_prediction = {}
        for key in keys:
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            if isinstance(all_predictions[0][key], tuple):
                tuple_of_lists = list(zip(*[[p.cpu() for p in tpl[key]] for tpl in all_predictions]))
                final_prediction[key] = tuple(torch.cat(l) for l in tuple_of_lists)
            else:
                final_prediction[key] = torch.cat([p[key].cpu() for p in all_predictions])
        if output_features:
            return final_prediction, features
        return final_prediction

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        request.model_kwargs["output_hidden_states"] = True
        predictions, features = self._predict(request, output_features=True)
        # We remove hidden_states from predictions!
        hidden_state = predictions.pop("hidden_states")[-1]
        attention_mask = features["attention_mask"]

        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        task_outputs = {
            "embedding_mode": embedding_mode
        }

        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}")

        if embedding_mode == "cls":
            emb = hidden_state[:, 0, :]
        # copied from sentence-transformers pooling
        elif embedding_mode == "max":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            hidden_state[input_mask_expanded == 0] = -1e9  # Set padding tokens to large negative value
            emb = torch.max(hidden_state, 1)[0]
        # copied from sentence-transformers pooling
        elif embedding_mode == "mean":
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
            sum_mask = input_mask_expanded.sum(1)
            emb = sum_embeddings / sum_mask
        elif embedding_mode == "token":
            emb = hidden_state
            task_outputs["word_ids"] = [features.word_ids(i) for i in range(len(request.input))]
        predictions["embeddings"] = emb

        return PredictionOutputForEmbedding(model_outputs=predictions, **task_outputs)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        label2id = self.model.config.label2id
        id2label = {v:k for k,v in label2id.items()}
        task_outputs = {
            "id2label": id2label,
            "word_ids": [features.word_ids(i) for i in range(len(request.input))]
        }
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForTokenClassification(model_outputs=predictions, **task_outputs)

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        predictions = self._predict(request)
        label2id = self.model.config.label2id
        id2label = {v:k for k,v in label2id.items()}
        task_outputs = {
            "id2label": id2label
        }
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForSequenceClassification(model_outputs=predictions, **task_outputs)

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get("padding", False)
        request.preprocessing_kwargs["add_special_tokens"] = request.preprocessing_kwargs.get("add_special_tokens", False)
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)
        # We cannot batch generate so we have to to it separately for each input prompt.
        for prompt in request.input:
            features = self.tokenizer(prompt, return_tensors="pt", **request.preprocessing_kwargs)
            input_ids = features["input_ids"]
            input_ids = self._ensure_tensor_on_device(input_ids=input_ids)["input_ids"]
            request.model_kwargs.update(request.task_kwargs)
            request.model_kwargs["return_dict_in_generate"] = True
            res = self.model.generate(input_ids, **request.model_kwargs)

            # put everything on CPU and add it to model_outputs
            for key in res.keys():
                if isinstance(res[key], tuple):
                    if isinstance(res[key][0], tuple):
                        res[key] = tuple((tuple(tensor.cpu() for tensor in tpl)) for tpl in res[key])
                    else:
                        res[key] = tuple(tensor.cpu() for tensor in res[key])
                else:
                    res[key] = res[key].cpu()
                model_outputs[key].append(res[key])

            generated_texts = [self.tokenizer.decode(seq, skip_special_tokens=True,
                                         clean_up_tokenization_spaces=request.task_kwargs.get("clean_up_tokenization_spaces", False))
                               for seq in res["sequences"]]
            task_outputs["generated_texts"].append(generated_texts)
        return PredictionOutputForGeneration(model_outputs=model_outputs, **task_outputs)

    def _question_answering(self, request: PredictionRequest) -> PredictionOutput:
        """
        Span-based question answering for a given question and context.

        We expect the input to use the (question, context) format for the text pairs.
        :param request:
        :return:
        """
        # Making heavy use of https://huggingface.co/transformers/_modules/transformers/pipelines/question_answering.html#QuestionAnsweringPipeline
        def decode(start_: np.ndarray, end_: np.ndarray, topk: int, max_answer_len: int, undesired_tokens_: np.ndarray) -> Tuple:
                """
                Take the output of any :obj:`ModelForQuestionAnswering` and will generate probabilities for each span to be the
                actual answer.

                In addition, it filters out some unwanted/impossible cases like answer len being greater than max_answer_len or
                answer end position being before the starting position. The method supports output the k-best answer through
                the topk argument.

                Args:
                    start_ (:obj:`np.ndarray`): Individual start probabilities for each token.
                    end (:obj:`np.ndarray`): Individual end_ probabilities for each token.
                    topk (:obj:`int`): Indicates how many possible answer span(s) to extract from the model output.
                    max_answer_len (:obj:`int`): Maximum size of the answer to extract from the model's output.
                    undesired_tokens_ (:obj:`np.ndarray`): Mask determining tokens that can be part of the answer
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
                desired_spans = np.isin(starts_, undesired_tokens_.nonzero()) & np.isin(ends_, undesired_tokens_.nonzero())
                starts_ = starts_[desired_spans]
                ends_ = ends_[desired_spans]
                scores_ = candidates[0, starts_, ends_]

                return starts_, ends_, scores_

        request.preprocessing_kwargs["truncation"] = "only_second"
        predictions, features = self._predict(request, output_features=True)

        task_outputs = {"answers": []}
        for idx, (start, end, (_, context)) in enumerate(zip(predictions["start_logits"], predictions["end_logits"], request.input)):
            start = start.numpy()
            end = end.numpy()
            # Ensure padded tokens & question tokens cannot belong to the set of candidate answers.
            question_tokens = np.abs(np.array([s != 1 for s in features.sequence_ids(idx)]) - 1)
            # Unmask CLS token for 'no answer'
            question_tokens[0] = 1
            undesired_tokens = question_tokens & features["attention_mask"][idx].numpy()

            # Generate mask
            undesired_tokens_mask = undesired_tokens == 0.0

            # Make sure non-context indexes in the tensor cannot contribute to the softmax
            start = np.where(undesired_tokens_mask, -10000.0, start)
            end = np.where(undesired_tokens_mask, -10000.0, end)

            start = np.exp(start - np.log(np.sum(np.exp(start), axis=-1, keepdims=True)))
            end = np.exp(end - np.log(np.sum(np.exp(end), axis=-1, keepdims=True)))

            # Get score for 'no answer' then mask for decoding step (CLS token
            no_answer_score = (start[0] * end[0]).item()
            start[0] = end[0] = 0.0

            starts, ends, scores = decode(
                start, end, request.task_kwargs.get("topk", 1), request.task_kwargs.get("max_answer_len", 128), undesired_tokens
            )
            enc = features[idx]
            answers = [
                {
                    "score": score.item(),
                    "start": enc.word_to_chars(
                        enc.token_to_word(s), sequence_index=1)[0],
                    "end": enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1],
                    "answer": context[
                              enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[0] :
                              enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1]],
                }
                for s, e, score in zip(starts, ends, scores)]
            answers.append({"score": no_answer_score, "start": 0, "end": 0, "answer": ""})
            answers = sorted(answers, key=lambda x: x["score"], reverse=True)[: request.task_kwargs.get("topk", 1)]
            task_outputs["answers"].append(answers)
        return PredictionOutputForQuestionAnswering(model_outputs=predictions, **task_outputs)

    async def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")
        if len(request.input) > self.max_input_size:
            raise ValueError(f"Input is too large. Max input size is {self.max_input_size}")

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

