from abc import ABC
from collections import defaultdict

from transformers import AutoTokenizer

from .transformer import Transformer
import torch
from torch.nn import functional as F
import onnxruntime
import numpy as np
from typing import Union, Tuple
from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import PredictionOutput, PredictionOutputForEmbedding, \
    PredictionOutputForSequenceClassification, PredictionOutputForGeneration, PredictionOutputForTokenClassification


def to_numpy(x):
    if type(x) is not np.ndarray:
        x = x.detach().cpu().numpy() if x.requires_grad else x.cpu().numpy()
    return x


class Onnx(Transformer):
    def __init__(self, model_path: str, model_name: str, batch_size: int, disable_gpu: bool,
                 max_input_size: int, **kwargs) -> None:
        # This assumes that a corresponding onnx file exists
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.session = onnxruntime.InferenceSession(model_path)
        if any("decoder" in model_input.name for model_input in self.session.get_inputs()) and self.tokenizer.bos_token is None:
            self.tokenizer.bos_token = self.tokenizer.pad_token
        self.batch_size = batch_size
        self.diable_gpu = disable_gpu
        self.max_input_size = max_input_size

    def _predict(self, request: PredictionRequest, output_features=False, features=None) \
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
        if features is None:
            features = self.tokenizer(request.input,
                                      return_tensors="pt",
                                      **request.preprocessing_kwargs)
        for start_idx in range(0, features["input_ids"].shape[0], self.batch_size):
            input_names = [self.session.get_inputs()[i].name for i in range(len(self.session.get_inputs()))]
            ort_inputs = dict(
                (k, to_numpy(input_data[start_idx:start_idx + self.batch_size])) for k, input_data in features.items()
                if k in input_names)
            if "decoder_input_ids" in input_names and "decoder_input_ids" not in features:
                # ToDo
                ort_inputs["decoder_input_ids"] = np.array([[self.tokenizer.bos_token_id] for _ in range(ort_inputs["input_ids"].shape[0])], dtype=np.int64)
                ort_inputs["decoder_attention_mask"] = np.array([[1] for _ in range(ort_inputs["input_ids"].shape[0])], dtype=np.int64)
            res = self.session.run([], ort_inputs)
            all_predictions.append(res)
        final_prediction = {}
        output_names = [self.session.get_outputs()[i].name for i in range(len(self.session.get_outputs()))]
        for idx, key in enumerate(output_names):
            # HuggingFace outputs for 'attentions' and more is returned as tuple of tensors
            # Tuple of tuples only exists for 'past_key_values' which is only relevant for generation.
            # Generation should NOT use this function
            final_prediction[key] = torch.cat([torch.tensor(p[idx]) for p in all_predictions])
        if output_features:
            return final_prediction, features
        return final_prediction

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        """
        Embeds the input from the request
        :param request: The request containing input and optionally task kwargs like embedding method
        :return: The embedding output
        """
        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}")

        task_outputs = {
            "embedding_mode": embedding_mode
        }
        predictions, features = self._predict(request, output_features=True)

        if embedding_mode == "pooler":
            if "pooler_output" not in predictions:
                raise ValueError("No pooler output available. Use a different model or an other embedding method")
            emb = predictions["pooler_output"]
        else:
            if "last_hidden_state" not in predictions:
                raise ValueError("No last hidden state available. Use a different model or the pooler embedding method")
            hidden_state = predictions["last_hidden_state"]
            attention_mask = features["attention_mask"]
            if embedding_mode == "cls":
                emb = hidden_state[:, 0, :]
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

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies the given input
        :param request: The request containing e.g. the input text
        :return: The prediction output contaiing the predicted labels
        """
        predictions = self._predict(request)
        task_outputs = {}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForSequenceClassification(model_outputs=predictions, **task_outputs)

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies each token of the input text
        :param request: The request containing e.g. the input text
        :return: the classification output containing the labels
        """
        predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        task_outputs = {
            "word_ids": [features.word_ids(i) for i in range(len(request.input))]
        }
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get("is_regression", False):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()

        return PredictionOutputForTokenClassification(model_outputs=predictions, **task_outputs)

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        """
        Generates a continuation for the given input sequence
        :param request: The request with e.g. the input sequence
        :return: The output containing the generated text
        """
        embedding_mode = request.task_kwargs.get("generation_mode", "greedy")
        max_length = request.task_kwargs.get("max_length", 20)
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)
        for prompt in request.input:
            if "num_beams" in request.task_kwargs:
                input_ids, scores = self._beam_search(request, prompt, max_length)

            else:
                input_ids, scores = self._greedy_generation(request, prompt, max_length)

            generated_texts = [self.tokenizer.decode(seq, skip_special_tokens=True,
                                                     clean_up_tokenization_spaces=request.task_kwargs.get(
                                                         "clean_up_tokenization_spaces", False))
                               for seq in input_ids]
            task_outputs["generated_texts"].append(generated_texts)

            res = {
                "sequence": input_ids,
                "scores": scores,
            }
            for key in res.keys():
                model_outputs[key].append(res[key])

        return PredictionOutputForGeneration(model_outputs=model_outputs, **task_outputs)

    def _greedy_generation(self, request, prompt, max_length):
        cur_len = 0
        eos_token_id = self.tokenizer.eos_token_id if self.tokenizer.eos_token_id is not None else self.tokenizer.pad_token_id
        request.preprocessing_kwargs["padding"] = False
        features = self.tokenizer(prompt,
                                  return_tensors="pt",
                                  **request.preprocessing_kwargs)
        input_ids = features["input_ids"]
        attention_mask = features["attention_mask"]
        unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
        scores = ()
        # greedy generation (adapted from transformers/generation_utils.py)
        while cur_len < max_length:
            features = {"input_ids": input_ids, "attention_mask": attention_mask}

            predictions = self._predict(request, features=features)

            next_token_logits = predictions["logits"][:, -1, :]
            scores += (next_token_logits,)

            # argmax
            next_tokens = torch.argmax(next_token_logits, dim=-1)

            # update generated ids, model inputs, and length for next step
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            attention_mask = torch.cat(
                [attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1
            )
            cur_len = cur_len + 1

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul((next_tokens != eos_token_id).long())

                # stop when each sentence is finished, or if we exceed the maximum length
            if unfinished_sequences.max() == 0:
                break
        return input_ids, scores

    def _prepare_input(self, encoder_features, decoder_sequence, encoder_decoder_model=False):
        model_input = encoder_features.copy()
        if encoder_decoder_model:
            if not decoder_sequence:
                model_input["decoder_input_ids"] = np.array([[self.tokenizer.eos_token]], dtype=np.int64)
                model_input["decoder_attention_mask"] = np.array([[0]], dtype=np.int64)
            else:
                model_input["decoder_input_ids"] = np.array([[decoder_sequence]], dtype=np.int64)
                model_input["decoder_attention_mask"] = np.array([1] * len(decoder_sequence), dtype=np.int64)

        elif decoder_sequence:
            model_input["input_ids"] = torch.cat((encoder_features["input_ids"], torch.tensor(decoder_sequence).unsqueeze(dim=0)), dim=1)
            model_input["attention_mask"] = torch.ones(model_input["input_ids"].shape, dtype=torch.int64)

        return model_input

    def _beam_search(self, request, prompt, max_length, **kwargs):
        cur_len = 0
        eos_token_id = self.tokenizer.eos_token_id if self.tokenizer.eos_token_id is not None else self.tokenizer.pad_token_id
        request.preprocessing_kwargs["padding"] = False
        features = self.tokenizer(prompt,
                                  return_tensors="pt",
                                  **request.preprocessing_kwargs)
        num_beams = request.task_kwargs.pop("num_beams")
        no_repeat_ngram_size = request.task_kwargs.pop("no_repeat_ngram_size", 0)
        sequences = [([], 0.0)]
        while cur_len < max_length:
            candidates = []

            for seq in sequences:
                model_input = self._prepare_input(features, seq[0])
                predictions = self._predict(request, False, model_input)

                next_token_logits = predictions["logits"][:, -1, :]
                next_token_scores = F.softmax(next_token_logits, dim=1)

                if no_repeat_ngram_size > 0:
                    banned_batch_tokens = calc_banned_ngram_tokens(
                        torch.tensor([seq[0]]), 1, no_repeat_ngram_size, cur_len
                    )
                    for i, banned_tokens in enumerate(banned_batch_tokens):
                        next_token_scores[i, banned_tokens] = -float("inf")

                # argmax
                next_token_prob, next_tokens_idx = torch.topk(next_token_scores, num_beams, dim=-1)
                candidates += [(seq[0] + [token_id], seq[1] + np.log(score)) for token_id, score in zip(next_tokens_idx.squeeze().tolist(), next_token_prob.squeeze().tolist())]

            sequences = sorted(candidates, key=lambda x: x[1], reverse=True)[:num_beams]
            cur_len += 1

        num_return_sequences = request.task_kwargs.pop("num_return_sequences", num_beams)
        if num_return_sequences > num_beams:
            raise ValueError("Expected: num_return_sequences <= num_beams, Got: {}, {}".format(num_return_sequences, num_beams))
        sequences = sequences[:num_return_sequences]

        return [torch.cat((features["input_ids"][0], torch.tensor(s[0]))) for s in sequences], [s[1] for s in sequences]


def calc_banned_ngram_tokens(prev_input_ids, num_hypos: int, no_repeat_ngram_size: int, cur_len: int) -> None:
    """Copied from fairseq for no_repeat_ngram in beam_search"""
    if cur_len + 1 < no_repeat_ngram_size:
        # return no banned tokens if we haven't generated no_repeat_ngram_size tokens yet
        return [[] for _ in range(num_hypos)]
    generated_ngrams = [{} for _ in range(num_hypos)]
    for idx in range(num_hypos):
        gen_tokens = prev_input_ids[idx].tolist()
        generated_ngram = generated_ngrams[idx]
        for ngram in zip(*[gen_tokens[i:] for i in range(no_repeat_ngram_size)]):
            prev_ngram_tuple = tuple(ngram[:-1])
            generated_ngram[prev_ngram_tuple] = generated_ngram.get(prev_ngram_tuple, []) + [ngram[-1]]

    def _get_generated_ngrams(hypo_idx):
        # Before decoding the next token, prevent decoding of ngrams that have already appeared
        start_idx = cur_len + 1 - no_repeat_ngram_size
        ngram_idx = tuple(prev_input_ids[hypo_idx, start_idx:cur_len].tolist())
        return generated_ngrams[hypo_idx].get(ngram_idx, [])

    banned_tokens = [_get_generated_ngrams(hypo_idx) for hypo_idx in range(num_hypos)]
    return banned_tokens

