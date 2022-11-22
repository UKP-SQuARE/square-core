from collections import defaultdict
from typing import Tuple, Union

import numpy as np
import onnxruntime
import torch
from tasks.config.model_config import model_config
from tasks.models.prediction import (PredictionOutput,
                                     PredictionOutputForEmbedding,
                                     PredictionOutputForGeneration,
                                     PredictionOutputForSequenceClassification,
                                     PredictionOutputForTokenClassification,
                                     PredictionOutputForQuestionAnswering)
from tasks.models.request import PredictionRequest
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer, AutoModel

from .transformer import Transformer

from optimum.onnxruntime import ORTModelForFeatureExtraction as ORTModelForFeatureExtraction_model
from optimum.onnxruntime import  (
    ORTModelForQuestionAnswering,
    ORTModelForSequenceClassification,
    ORTModelForTokenClassification,
    ORTModelForSeq2SeqLM
)


from transformers.modeling_outputs import (
    BaseModelOutputWithPooling,

)
from typing import Any, Dict, List, Optional, Union


class ORTModelForFeatureExtraction(ORTModelForFeatureExtraction_model):
    '''

    The ORTModelForFeatureExtraction from hugging face disabled the pooler_output.
     Rewrite this class to enable it.
     https://huggingface.co/docs/transformers/main_classes/output
     https://github.com/huggingface/optimum/blob/v1.4.1/optimum/onnxruntime/modeling_ort.py#L434
    '''

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        **kwargs,
    ):
        # converts pytorch inputs into numpy inputs for onnx
        onnx_inputs = {
            "input_ids": input_ids.cpu().detach().numpy(),
            "attention_mask": attention_mask.cpu().detach().numpy(),
        }
        if token_type_ids is not None:
            onnx_inputs["token_type_ids"] = token_type_ids.cpu().detach().numpy()
        # run inference
        outputs = self.model.run(None, onnx_inputs)
        print(f"output of ORT EctModel:{outputs}")
        print(f"self.model_outpus:{self.model_outputs}")
        last_hidden_state = torch.from_numpy(outputs[self.model_outputs["last_hidden_state"]]).to(self.device)
        pooler_output = torch.from_numpy(outputs[self.model_outputs["pooler_output"]]).to(self.device)
        # converts output to namedtuple for pipelines post-processing
        return BaseModelOutputWithPooling(last_hidden_state=last_hidden_state,pooler_output=pooler_output)




def to_numpy(x):
    if type(x) is not np.ndarray:
        x = x.detach().cpu().numpy() if x.requires_grad else x.cpu().numpy()
    return x


class Onnx(Transformer):
    def __init__(self, **kwargs) -> None:

        """
         Args:
             model_path: path where the model is stored
             model_name: the ONNX model name
             decoder_path: path to the decoder ONNX model
             kwargs: Not used
        """
        # This assumes that a corresponding onnx file exists
        self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        # self.session = onnxruntime.InferenceSession(model_config.model_path)
        # self._load_model(AutoModel,model_config.model_name,model_config.disable_gpu)
        # # check whether a decoder model is available
        self.is_encoder_decoder = (
            model_config.decoder_path is not None and model_config.decoder_path != ""
        )
        # if self.is_encoder_decoder:
        #     # if available load the decoder model in a onnx session
        #     self.decoder_session = onnxruntime.InferenceSession(
        #         model_config.decoder_path
        #     )

    # def _predict(
    #     self, request: PredictionRequest, output_features=False, features=None
    # ) -> Union[dict, Tuple[dict, dict]]:
    #     """
    #     Inference on the input.
    #
    #     Args:
    #
    #          request: the request with the input and optional kwargs
    #          output_features: return the features of the input. Necessary if, e.g., attention mask is needed for post-processing.
    #
    #     Returns:
    #             The model outputs and optionally the input features
    #     """
    #     all_predictions = []
    #     request.preprocessing_kwargs["padding"] = request.preprocessing_kwargs.get(
    #         "padding", True
    #     )
    #     request.preprocessing_kwargs["truncation"] = request.preprocessing_kwargs.get(
    #         "truncation", True
    #     )
    #     if features is None:
    #         features = self.tokenizer(
    #             request.input, return_tensors="pt", **request.preprocessing_kwargs
    #         )
    #     embedding_model = ORTModelForFeatureExtraction(self.session)
    #     final_prediction = embedding_model(**features)
    #
    #
    #     if output_features:
    #         return final_prediction, features
    #     return final_prediction
    #

    def _embedding(self, request: PredictionRequest) -> PredictionOutput:
        """
        Embeds the input from the request

        Args:
             request: The request containing input and optionally task kwargs like embedding method

        Return:
             The embedding output
        """
        embedding_mode = request.task_kwargs.get("embedding_mode", "mean")
        if embedding_mode not in self.SUPPORTED_EMBEDDING_MODES:
            raise ValueError(
                f"Embedding mode {embedding_mode} not in list of supported modes {self.SUPPORTED_EMBEDDING_MODES}"
            )

        task_outputs = {"embedding_mode": embedding_mode}
        # predictions, features = self._predict(request, output_features=True)
        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        embedding_model = ORTModelForFeatureExtraction.from_pretrained(model_config.model_path)
        # embedding_model = ORTModelForFeatureExtraction(self.session)
        predictions = embedding_model(**features)

        if embedding_mode == "pooler":
            if "pooler_output" not in predictions:
                raise ValueError(
                    "No pooler output available. Use a different model or an other embedding method"
                )
            emb = predictions["pooler_output"]
        else:
            if "last_hidden_state" not in predictions:
                if "hidden_states" in predictions:
                    hidden_state = predictions["hidden_states"]
                else:
                    raise ValueError(
                        "No last hidden state available. Use a different model or the pooler embedding method"
                    )
            else:
                hidden_state = predictions["last_hidden_state"]
            attention_mask = features["attention_mask"]
            if embedding_mode == "cls":
                emb = hidden_state[:, 0, :]
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

    def _question_answering(self, request: PredictionRequest) -> PredictionOutput:
        '''

        Answer the given questions.


        Args:
             request: The request containing e.g. the input text

        Returns:
                 The prediction output containing the predicted labels

        '''
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
            desired_spans = np.isin(starts_, undesired_tokens_.nonzero()) & np.isin(ends_, undesired_tokens_.nonzero())
            starts_ = starts_[desired_spans]
            ends_ = ends_[desired_spans]
            scores_ = candidates[0, starts_, ends_]

            return starts_, ends_, scores_

        print("******QA Task*******")
        print(f"request:{request}")
        qa_model= ORTModelForQuestionAnswering.from_pretrained(model_config.model_path)
        # model_qa = ORTModelForQuestionAnswering(self.session)

        # self.model = model_qa

        request.preprocessing_kwargs["truncation"] = "only_second"

        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        # predictions, features = self._predict(request, output_features=True)
        # print(f"predictions from _predict():{predictions}")

        predictions = qa_model(**features)
        print(f"predictions from qa_model:{predictions}")
        # predictions['attentions'] = torch.ones([1,1,12,16,16])
        print(f"prediction:{predictions}")
        print(f"features:{features}")

        task_outputs = {
            "answers": [],
            "attributions": [],
            "adversarial": {
                "indices": [],
            },  # for hotflip, input_reduction and topk
        }
        # for idx, (start, end, (_, context)) in enumerate(
        #         zip(predictions["start_logits"], predictions["end_logits"], request.input)
        # ):
        #     start = start.numpy()
        #     end = end.numpy()
        #     # Ensure padded tokens & question tokens cannot
        #     # belong to the set of candidate answers.
        #     question_tokens = np.abs(np.array([s != 1 for s in features.sequence_ids(idx)]) - 1)
        #     # Unmask CLS token for 'no answer'
        #     question_tokens[0] = 1
        #     undesired_tokens = question_tokens & features["attention_mask"][idx].numpy()
        #
        #     # Generate mask
        #     undesired_tokens_mask = undesired_tokens == 0.0
        #
        #     # Make sure non-context indexes in the tensor cannot
        #     # contribute to the softmax
        #     start = np.where(undesired_tokens_mask, -10000.0, start)
        #     end = np.where(undesired_tokens_mask, -10000.0, end)
        #
        #     start = np.exp(start - np.log(np.sum(np.exp(start), axis=-1, keepdims=True)))
        #     end = np.exp(end - np.log(np.sum(np.exp(end), axis=-1, keepdims=True)))
        #
        #     # Get score for 'no answer' then mask for decoding step (CLS token
        #     no_answer_score = (start[0] * end[0]).item()
        #     start[0] = end[0] = 0.0
        #
        #     starts, ends, scores = decode(
        #         start,
        #         end,
        #         request.task_kwargs.get("topk", 1),
        #         request.task_kwargs.get("max_answer_len", 128),
        #         undesired_tokens,
        #     )
        #     enc = features[idx]
        #     self.original_ans_start = enc.token_to_word(starts[0])
        #     self.original_ans_end = enc.token_to_word(ends[0])
        #     answers = [
        #         {
        #             "score": score.item(),
        #             "start": enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[0],
        #             "end": enc.word_to_chars(enc.token_to_word(e), sequence_index=1)[1],
        #             "answer": context[
        #                       enc.word_to_chars(enc.token_to_word(s), sequence_index=1)[0]: enc.word_to_chars(
        #                           enc.token_to_word(e), sequence_index=1
        #                       )[1]
        #                       ],
        #         }
        #         for s, e, score in zip(starts, ends, scores)
        #     ]
        #     if request.task_kwargs.get("show_null_answers", True):
        #         answers.append({"score": no_answer_score, "start": 0, "end": 0, "answer": ""})
        #     answers = sorted(answers, key=lambda x: x["score"], reverse=True)[: request.task_kwargs.get("topk", 1)]
        #     task_outputs["answers"].append(answers)
        #
        #     # word attributions
        #     if request.explain_kwargs or request.attack_kwargs:
        #         start_idx = torch.argmax(predictions["start_logits"])
        #         end_idx = torch.argmax(predictions["end_logits"])
        #         answer_start = torch.tensor([start_idx])
        #         answer_end = torch.tensor([end_idx])
        #
        #         grad_kwargs = {
        #             "start_positions": answer_start.to(self.model.device),
        #             "end_positions": answer_end.to(self.model.device),
        #         }
        #         attributions = self._interpret(
        #             request=request,
        #             prediction=predictions,
        #             method=request.explain_kwargs["method"]
        #             if request.explain_kwargs
        #             else request.attack_kwargs["saliency_method"],
        #             **grad_kwargs,
        #         )
        #         # new added section start
        #         # to extract the name of the attack method
        #         attack_method = None
        #         if request.attack_kwargs:
        #             for k, v in request.attack_kwargs.items():
        #                 if k == "method":
        #                     attack_method = v
        #         # new added section end
        #         word_imp = self.process_outputs(
        #             attributions=attributions,
        #             top_k=request.explain_kwargs["top_k"] if request.explain_kwargs else 10,
        #             mode=request.explain_kwargs["mode"] if request.explain_kwargs else "all",
        #             task="question_answering",
        #             # new added paramter in process_ourput method
        #             attack_method=attack_method,
        #         )
        #         # print(word_imp)
        #         task_outputs["attributions"] = word_imp
        #
        #     if (
        #             not request.attack_kwargs
        #             and not request.explain_kwargs
        #             and not request.model_kwargs.get("output_attentions", False)
        #     ):
        #         # predictions.pop("attentions", None)
        #         pass
        #
        #     if request.attack_kwargs:
        #         new_predictions = self._model_attacks(request, task_outputs)
        #         return new_predictions

        return PredictionOutputForQuestionAnswering(model_outputs=predictions, **task_outputs)

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies the given input

        Args:
             request: The request containing e.g. the input text

        Returns:
                 The prediction output containing the predicted labels
        """
        # predictions = self._predict(request)

        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        seq_model=ORTModelForSequenceClassification.from_pretrained(model_config.model_path)

        predictions=seq_model(**features)

        task_outputs = {}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if predictions["logits"].size()[-1] != 1 and not request.task_kwargs.get(
            "is_regression", False
        ):
            probabilities = torch.softmax(predictions["logits"], dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(
                predictions["logits"], dim=-1
            ).tolist()

        return PredictionOutputForSequenceClassification(
            model_outputs=predictions, **task_outputs
        )

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies each token of the input text

        Args:
            request: The request containing e.g. the input text

        Returns:
                 the classification output containing the labels
        """
        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        tok_model=ORTModelForTokenClassification.from_pretrained(model_config.model_path)
        print(f"features of TOK:{features}")

        predictions=tok_model(**features)
        # predictions, features = self._predict(request, output_features=True)
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        task_outputs = {
            "word_ids": [features.word_ids(i) for i in range(len(request.input))]
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

    def _generation(self, request: PredictionRequest) -> PredictionOutput:
        """
        Generates a continuation for the given input sequence

        Args:
             request: The request with e.g. the input sequence

        Returns:
             The output containing the generated text
        """
        max_length = request.task_kwargs.get("max_length", 20)
        task_outputs = {"generated_texts": []}
        model_outputs = defaultdict(list)
        features = self.tokenizer(
            request.input, return_tensors="pt", **request.preprocessing_kwargs
        )
        gen_model = ORTModelForSeq2SeqLM.from_pretrained(model_config.model_path)

        for prompt in request.input:
            # if num_beams is specified beam search is executed otherwise greedy search
            if "num_beams" in request.task_kwargs:
                print("*****Beam Search*****")
                print(f"task_kwargs:{request.task_kwargs}")
                outputs = gen_model.generate(features.input_ids, num_beams=request.task_kwargs["num_beams"])
                generated_texts = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                # input_ids, scores = self._beam_search(request, prompt, max_length)
            else:
                print("*****Greedy Search*****")

                outputs = gen_model.generate(features.input_ids, do_sample=True, max_length=max_length)
                generated_texts = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                # input_ids, scores = self._greedy_generation(request, prompt, max_length)

            # generated_texts = [
            #     self.tokenizer.decode(
            #         seq,
            #         skip_special_tokens=True,
            #         clean_up_tokenization_spaces=request.task_kwargs.get(
            #             "clean_up_tokenization_spaces", False
            #         ),
            #     )
            #     for seq in input_ids
            # ]
            task_outputs["generated_texts"].append(generated_texts)

            res = {
                "sequence": features.input_ids,
                # "scores": scores,
            }
            for key in res.keys():
                model_outputs[key].append(res[key])
        print(f"Model output:{model_outputs}")
        model_outputs = {}
        print(f"task outputs: {task_outputs}")

        return PredictionOutputForGeneration(
            model_outputs=model_outputs, **task_outputs
        )

    # def _greedy_generation(self, request, prompt, max_length):
    #     """
    #     Performs greedy generation for the prompts
    #
    #     Args:
    #          request: the inference request
    #          prompt: the prompt for the generation
    #          max_length: the maximum length of the generated sequence
    #     Returns:
    #          the ids of the generated sequence and the score
    #     """
    #     cur_len = 0
    #     eos_token_id = (
    #         self.tokenizer.eos_token_id
    #         if self.tokenizer.eos_token_id is not None
    #         else self.tokenizer.pad_token_id
    #     )
    #     request.preprocessing_kwargs["padding"] = False
    #     features = self.tokenizer(
    #         prompt, return_tensors="pt", **request.preprocessing_kwargs
    #     )
    #     input_ids = features["input_ids"]
    #     generated_ids = [self.get_bos_token()] if self.is_encoder_decoder else []
    #     unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
    #     scores = ()
    #     # greedy generation (adapted from transformers/generation_utils.py)
    #     while cur_len < max_length:
    #         input_data = self._prepare_input(features, generated_ids)
    #         predictions = self._predict(request, features=input_data)
    #
    #         next_token_logits = predictions["logits"][:, -1, :]
    #         scores += (next_token_logits,)
    #
    #         # argmax
    #         next_tokens = torch.argmax(next_token_logits, dim=-1)
    #         # update generated ids, model inputs, and length for next step
    #         generated_ids.append(next_tokens[:, None].item())
    #         cur_len = cur_len + 1
    #
    #         if eos_token_id is not None:
    #             unfinished_sequences = unfinished_sequences.mul(
    #                 (next_tokens != eos_token_id).long()
    #             )
    #             # stop when each sentence is finished, or if we exceed the maximum length
    #         if unfinished_sequences.max() == 0:
    #             break
    #     return [generated_ids], scores
    #
    # def _prepare_input(self, encoder_features, generated_sequence):
    #     """
    #     Prepares the input for the _predict method. If the model is an encoder decoder model the
    #     generated sequence is the decoder input.
    #
    #     Args:
    #          encoder_features: the features of the prompt
    #          generated_sequence: the generated ids
    #
    #     Returns:
    #          the features for the model
    #     """
    #     model_input = encoder_features.copy()
    #     # if it is a encoder decoder model the generated sequence is passed to the decoder
    #     # otherwise the generated sequence is appended to the input_ids
    #     if self.is_encoder_decoder:
    #         model_input["decoder_input_ids"] = np.array(
    #             [generated_sequence], dtype=np.int64
    #         )
    #         model_input["decoder_attention_mask"] = np.array(
    #             [[1] * len(generated_sequence)], dtype=np.int64
    #         )
    #
    #     elif generated_sequence:
    #         model_input["input_ids"] = torch.cat(
    #             (
    #                 encoder_features["input_ids"],
    #                 torch.tensor(generated_sequence).unsqueeze(dim=0),
    #             ),
    #             dim=1,
    #         )
    #         model_input["attention_mask"] = torch.ones(
    #             model_input["input_ids"].shape, dtype=torch.int64
    #         )
    #
    #     return model_input
    #
    # def _beam_search(self, request, prompt, max_length):
    #     """
    #     Performs beam search for the given prompt
    #
    #     Args:
    #          request: the inference request
    #          prompt: the generation prompt
    #          max_length: the maximum length of the generated sequence
    #
    #     Returns:
    #          the generated sequence(s)
    #     """
    #     request.preprocessing_kwargs["padding"] = False
    #     features = self.tokenizer(
    #         prompt, return_tensors="pt", **request.preprocessing_kwargs
    #     )
    #     # get the generation arguments
    #     num_beams = request.task_kwargs.pop("num_beams")
    #     no_repeat_ngram_size = request.task_kwargs.pop("no_repeat_ngram_size", 0)
    #     do_sample = request.task_kwargs.pop("do_sample", False)
    #     top_p = request.task_kwargs.pop("top_p", None)
    #     top_k = request.task_kwargs.pop("top_k", None)
    #     num_return_sequences = request.task_kwargs.pop("num_return_sequences", 1)
    #     return_sequences = []
    #     for i in range(num_return_sequences):
    #         sequences = [
    #             ([self.get_bos_token()] if self.is_encoder_decoder else [], 0.0)
    #         ]
    #         cur_len = 0
    #         while cur_len < max_length:
    #             candidates = []
    #             for seq in sequences:
    #                 model_input = self._prepare_input(features, seq[0])
    #                 predictions = self._predict(request, False, model_input)
    #
    #                 next_token_logits = predictions["logits"][:, -1, :]
    #                 next_token_scores = F.softmax(next_token_logits, dim=1)
    #                 if do_sample:
    #                     next_token_scores = self._preprocess_logits(
    #                         next_token_scores,
    #                         top_k=top_k,
    #                         top_p=top_p,
    #                         min_tokens_to_keep=2 * num_beams,
    #                     )
    #
    #                 if no_repeat_ngram_size > 0:
    #                     banned_batch_tokens = calc_banned_ngram_tokens(
    #                         torch.tensor([seq[0]]), 1, no_repeat_ngram_size, cur_len
    #                     )
    #                     for i, banned_tokens in enumerate(banned_batch_tokens):
    #                         next_token_scores[i, banned_tokens] = -float("inf")
    #
    #                 if do_sample:
    #                     # draw the next token based on the probabilities
    #                     probs = nn.functional.softmax(next_token_scores, dim=-1)
    #
    #                     next_tokens = torch.multinomial(
    #                         probs, num_samples=2 * num_beams
    #                     )
    #                     next_token_prob = torch.gather(
    #                         next_token_scores, -1, next_tokens
    #                     )
    #
    #                     _, _indices = torch.sort(
    #                         next_token_prob, descending=True, dim=1
    #                     )
    #                     next_tokens_idx = torch.gather(next_tokens, -1, _indices)
    #
    #                 else:
    #                     # take the most likely tokens as the next tokens
    #                     next_token_prob, next_tokens_idx = torch.topk(
    #                         next_token_scores, num_beams, dim=-1
    #                     )
    #                 candidates += [
    #                     (seq[0] + [token_id], seq[1] + np.log(score))
    #                     for token_id, score in zip(
    #                         next_tokens_idx.squeeze().tolist(),
    #                         next_token_prob.squeeze().tolist(),
    #                     )
    #                 ]
    #             # select the candidates with the highest scores as beams for the generation of the next token
    #             sequences = sorted(candidates, key=lambda x: x[1], reverse=True)[
    #                 :num_beams
    #             ]
    #             cur_len += 1
    #
    #         return_sequences.append(sequences[0])
    #
    #     return (
    #         [torch.tensor(s[0]) for s in return_sequences],
    #         [s[1] for s in return_sequences],
    #     )
    #
    # def get_bos_token(self):
    #     """
    #     Depending on the model the beginning of sentence token id can be different or not provided.
    #
    #     Returns:
    #          beginning of sentence token id
    #     """
    #     if self.tokenizer.bos_token_id is not None:
    #         return self.tokenizer.bos_token_id
    #     # if no bos token is available use the padding token
    #     else:
    #         return self.tokenizer.pad_token_id
    #
    # def _preprocess_logits(
    #     self,
    #     scores,
    #     top_k=None,
    #     top_p=None,
    #     min_tokens_to_keep=1,
    #     filter_value=-float("Inf"),
    # ):
    #     """
    #     Sets the scores for all tokens that are not in top_p and top_k to the filter value (default = -inf).
    #     Adapted from huggingface/transformers/generation_logits_process.py
    #
    #     Args:
    #          scores:the initial scores for each token
    #          top_k: the top_k threshold
    #          top_p: the top_p threshold
    #          min_tokens_to_keep: the min_number_of_tokens_to_keep
    #          filter_value: the value to replace the scores with
    #
    #     Returns:
    #          the processed scores
    #     """
    #     if top_k is not None and top_k != 0:
    #         top_k = min(max(top_k, min_tokens_to_keep), scores.size(-1))  # Safety check
    #         # Remove all tokens with a probability less than the last token of the top-k
    #         indices_to_remove = scores < torch.topk(scores, top_k)[0][..., -1, None]
    #         scores = scores.masked_fill(indices_to_remove, filter_value)
    #     if top_p is not None and top_p < 1.0:
    #         sorted_logits, sorted_indices = torch.sort(scores, descending=True)
    #         cumulative_probs = sorted_logits.softmax(dim=-1).cumsum(dim=-1)
    #
    #         # Remove tokens with cumulative top_p above the threshold (token with 0 are kept)
    #         sorted_indices_to_remove = cumulative_probs > top_p
    #         if min_tokens_to_keep > 1:
    #             # Keep at least min_tokens_to_keep (set to min_tokens_to_keep-1 because we add the first one below)
    #             sorted_indices_to_remove[..., : min_tokens_to_keep - 1] = 0
    #         # Shift the indices to the right to keep also the first token above the threshold
    #         sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[
    #             ..., :-1
    #         ].clone()
    #         sorted_indices_to_remove[..., 0] = 0
    #
    #         # scatter sorted tensors to original indexing
    #         indices_to_remove = sorted_indices_to_remove.scatter(
    #             1, sorted_indices, sorted_indices_to_remove
    #         )
    #         scores = scores.masked_fill(indices_to_remove, filter_value)
    #
    #     return scores

#
# def calc_banned_ngram_tokens(
#     prev_input_ids, num_hypos: int, no_repeat_ngram_size: int, cur_len: int
# ) -> None:
#     """Copied from fairseq for no_repeat_ngram in beam_search"""
#     if cur_len + 1 < no_repeat_ngram_size:
#         # return no banned tokens if we haven't generated no_repeat_ngram_size tokens yet
#         return [[] for _ in range(num_hypos)]
#     generated_ngrams = [{} for _ in range(num_hypos)]
#     for idx in range(num_hypos):
#         gen_tokens = prev_input_ids[idx].tolist()
#         generated_ngram = generated_ngrams[idx]
#         for ngram in zip(*[gen_tokens[i:] for i in range(no_repeat_ngram_size)]):
#             prev_ngram_tuple = tuple(ngram[:-1])
#             generated_ngram[prev_ngram_tuple] = generated_ngram.get(
#                 prev_ngram_tuple, []
#             ) + [ngram[-1]]
#
#     def _get_generated_ngrams(hypo_idx):
#         # Before decoding the next token, prevent decoding of ngrams that have already appeared
#         start_idx = cur_len + 1 - no_repeat_ngram_size
#         ngram_idx = tuple(prev_input_ids[hypo_idx, start_idx:cur_len].tolist())
#         return generated_ngrams[hypo_idx].get(ngram_idx, [])
#
#     banned_tokens = [_get_generated_ngrams(hypo_idx) for hypo_idx in range(num_hypos)]
#     return banned_tokens
