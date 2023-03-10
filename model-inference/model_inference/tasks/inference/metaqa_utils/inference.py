from transformers import AutoTokenizer
from metaqa_utils.MetaQA_Model import MetaQA_Model
import numpy as np

import torch


class PredictionRequest:
    input_question: str
    input_predictions: list[(str, float)]


class MetaQA_basemodel:
    def __init__(self, path_to_model):
        self.metaqa_model = MetaQA_Model.from_pretrained(path_to_model)
        self.tokenizer = AutoTokenizer.from_pretrained(path_to_model)

    def run_metaqa(self, request: PredictionRequest):
        """
        Runs MetaQA on a single instance.
        """
        # Encode instance
        input_ids, token_ids, attention_masks, ans_sc = self._encode_metaQA_instance(
            request
        )
        # Run model
        logits = self.metaqa_model(input_ids, token_ids, attention_masks, ans_sc).logits
        # Get predictions
        (pred, agent_name, metaqa_score, agent_score) = self._get_predictions(
            logits.detach().numpy(), request.input_predictions
        )
        return (pred, agent_name, metaqa_score, agent_score)

    def _encode_metaQA_instance(self, request: PredictionRequest, max_len=512):
        """
        Creates input ids, token ids, token masks for an instance of MetaQA.
        """
        # Create input ids, token ids, and masks
        list_input_ids = []
        list_token_ids = []
        list_attention_masks = []
        list_ans_sc = []

        # Process question
        ## input ids
        list_input_ids.extend(
            self.tokenizer.encode("[CLS]", add_special_tokens=False)
        )  # [CLS]
        list_input_ids.extend(
            self.tokenizer.encode(request.input_question, add_special_tokens=False)
        )  # Query token ids
        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # [SEP]
        ## token ids
        list_token_ids.extend(len(list_input_ids) * [0])
        ## ans_sc_ids
        list_ans_sc.extend(len(list_input_ids) * [0])

        # Process qa_agents predictions
        for qa_agent_pred in request.input_predictions:
            ## input ids
            list_input_ids.append(1)  # [RANK]
            ans_input_ids = self.tokenizer.encode(
                qa_agent_pred[0], add_special_tokens=False
            )
            list_input_ids.extend(ans_input_ids)
            ## token ids
            list_token_ids.extend(
                (len(ans_input_ids) + 1) * [1]
            )  # +1 to account for [RANK]
            ## ans_sc ids
            ans_score = qa_agent_pred[1]
            list_ans_sc.extend(
                (len(ans_input_ids) + 1) * [ans_score]
            )  # +1 to account for [RANK]
        # Last [SEP]
        # input ids
        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # last [SEP]
        # token ids
        list_token_ids.append(1)
        # ans_sc_ids
        list_ans_sc.append(0)
        # attention masks
        list_attention_masks.extend(len(list_input_ids) * [1])

        # PADDING
        len_padding = max_len - len(list_input_ids)
        ## inputs ids
        list_input_ids.extend([0] * len_padding)  # [PAD]
        ## token ids
        list_token_ids.extend((len(list_input_ids) - len(list_token_ids)) * [1])
        ## ans_sc_ids
        list_ans_sc.extend((len(list_input_ids) - len(list_ans_sc)) * [0])
        ## attention masks
        list_attention_masks.extend(
            (len(list_input_ids) - len(list_attention_masks)) * [0]
        )

        list_input_ids = torch.Tensor(list_input_ids).unsqueeze(0).long()
        list_token_ids = torch.Tensor(list_token_ids).unsqueeze(0).long()
        list_attention_masks = torch.Tensor(list_attention_masks).unsqueeze(0).long()
        list_ans_sc = torch.Tensor(list_ans_sc).unsqueeze(0).long()

        if len(list_input_ids) > max_len:
            return None
        else:
            return (list_input_ids, list_token_ids, list_attention_masks, list_ans_sc)

    def _get_predictions(self, logits, input_predictions):
        top_k = lambda a, k: np.argsort(-a)[:k]
        for idx in top_k(logits[0][:, 1], self.metaqa_model.num_agents):
            pred = input_predictions[idx][0]
            if pred != "":
                agent_name = self.metaqa_model.config.agents[idx]
                metaqa_score = logits[0][idx][1]
                agent_score = input_predictions[idx][1]
                return (pred, agent_name, metaqa_score, agent_score)
        # no valid prediction found, return the best prediction
        idx = top_k(logits[0][:, 1], 1)[0]
        pred = input_predictions[idx][0]
        metaqa_score = logits[0][idx][1]
        agent_name = self.metaqa_model.config.agents[idx]
        agent_score = input_predictions[idx][1]
        return (pred, agent_name, metaqa_score, agent_score)


class MetaQA:
    def __init__(self, path_to_model):
        self.metaqa_model = MetaQA_Model.from_pretrained(path_to_model)
        self.tokenizer = AutoTokenizer.from_pretrained(path_to_model)

    def run_metaqa(self, request: PredictionRequest):
        """
        Runs MetaQA on a single instance.
        """
        # Encode instance
        input_ids, token_ids, attention_masks, ans_sc = self._encode_metaQA_instance(
            request
        )
        # Run model
        logits = self.metaqa_model(input_ids, token_ids, attention_masks, ans_sc).logits
        # Get predictions
        (pred, agent_name, metaqa_score, agent_score) = self._get_predictions(
            logits.detach().numpy(), request.input_predictions
        )
        return (pred, agent_name, metaqa_score, agent_score)

    def _encode_metaQA_instance(self, request: PredictionRequest, max_len=512):
        """
        Creates input ids, token ids, token masks for an instance of MetaQA.
        """
        # Create input ids, token ids, and masks
        list_input_ids = []
        list_token_ids = []
        list_attention_masks = []
        list_ans_sc = []

        # Process question
        ## input ids
        list_input_ids.extend(
            self.tokenizer.encode("[CLS]", add_special_tokens=False)
        )  # [CLS]
        list_input_ids.extend(
            self.tokenizer.encode(request.input_question, add_special_tokens=False)
        )  # Query token ids
        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # [SEP]
        ## token ids
        list_token_ids.extend(len(list_input_ids) * [0])
        ## ans_sc_ids
        list_ans_sc.extend(len(list_input_ids) * [0])

        # Process qa_agents predictions
        for qa_agent_pred in request.input_predictions:
            ## input ids
            list_input_ids.append(1)  # [RANK]
            ans_input_ids = self.tokenizer.encode(
                qa_agent_pred[0], add_special_tokens=False
            )
            list_input_ids.extend(ans_input_ids)
            ## token ids
            list_token_ids.extend(
                (len(ans_input_ids) + 1) * [1]
            )  # +1 to account for [RANK]
            ## ans_sc ids
            ans_score = qa_agent_pred[1]
            list_ans_sc.extend(
                (len(ans_input_ids) + 1) * [ans_score]
            )  # +1 to account for [RANK]
        # Last [SEP]
        # input ids
        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # last [SEP]
        # token ids
        list_token_ids.append(1)
        # ans_sc_ids
        list_ans_sc.append(0)
        # attention masks
        list_attention_masks.extend(len(list_input_ids) * [1])

        # PADDING
        len_padding = max_len - len(list_input_ids)
        ## inputs ids
        list_input_ids.extend([0] * len_padding)  # [PAD]
        ## token ids
        list_token_ids.extend((len(list_input_ids) - len(list_token_ids)) * [1])
        ## ans_sc_ids
        list_ans_sc.extend((len(list_input_ids) - len(list_ans_sc)) * [0])
        ## attention masks
        list_attention_masks.extend(
            (len(list_input_ids) - len(list_attention_masks)) * [0]
        )

        list_input_ids = torch.Tensor(list_input_ids).unsqueeze(0).long()
        list_token_ids = torch.Tensor(list_token_ids).unsqueeze(0).long()
        list_attention_masks = torch.Tensor(list_attention_masks).unsqueeze(0).long()
        list_ans_sc = torch.Tensor(list_ans_sc).unsqueeze(0).long()

        if len(list_input_ids) > max_len:
            return None
        else:
            return (list_input_ids, list_token_ids, list_attention_masks, list_ans_sc)

    def _get_predictions(self, logits, input_predictions):
        top_k = lambda a, k: np.argsort(-a)[:k]
        for idx in top_k(logits[0][:, 1], self.metaqa_model.num_agents):
            pred = input_predictions[idx][0]
            if pred != "":
                agent_name = self.metaqa_model.config.agents[idx]
                metaqa_score = logits[0][idx][1]
                agent_score = input_predictions[idx][1]
                return (pred, agent_name, metaqa_score, agent_score)
        # no valid prediction found, return the best prediction
        idx = top_k(logits[0][:, 1], 1)[0]
        pred = input_predictions[idx][0]
        metaqa_score = logits[0][idx][1]
        agent_name = self.metaqa_model.config.agents[idx]
        agent_score = input_predictions[idx][1]
        return (pred, agent_name, metaqa_score, agent_score)
