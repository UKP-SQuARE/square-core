import torch
from typing import List, Tuple
import numpy as np
from transformers import AutoTokenizer
from .metaqa_utils.MetaQA_Model import MetaQA_Model

# from metaqa_utils.inference import MetaQA_basemodel
from model_inference.tasks.inference.model import Model
from model_inference.tasks.config.model_config import model_config
from model_inference.tasks.models.prediction import (
    PredictionOutput,
    PredictionOutputForQuestionAnswering,
)
from model_inference.tasks.models.request import PredictionRequest, Task


class MetaQA(Model):
    def __init__(self, **kwargs) -> None:
        self.device = (
            "cuda"
            if torch.cuda.is_available() and not model_config.disable_gpu
            else "cpu"
        )
        self.metaqa_model = MetaQA_Model.from_pretrained(model_config.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        """
        Cover the function in parent model to run predict
        """
        if task == Task.question_answering:
            return self._question_answering(request)

    def _question_answering(self, request: PredictionRequest) -> PredictionOutput:
        """
        QA of MetaQA, the required field in request are
        question: str
        agents_predictions: the prediction from qa agents,

        """
        question: str = request.input["question"]
        topk: int = request.task_kwargs.get("topk", 1)
        agents_predictions: list = request.input["agents_predictions"]

        if len(agents_predictions) < 16:
            # TODO:how many agents?
            for i in range(16 - len(agents_predictions)):
                agents_predictions.append(["", 0.0])
        # agent_predictions = self._get_agents_prediction(question,context)
        pred_list = self._predict(question, agents_predictions, topk)

        task_outputs = {"answers": [[]]}
        for i in pred_list:
            pred = {}
            output_name = ["answer", "agent_name", "metaqa_score", "agent_score"]
            for key, value in zip(output_name, i):
                pred[key] = value
            task_outputs["answers"][0].append(pred)
        predictions = {}
        return PredictionOutputForQuestionAnswering(
            model_outputs=predictions, **task_outputs
        )

    def _predict(
        self, question: str, agents_predictions: List[Tuple[str, float]], topk
    ):
        """
        Runs MetaQA on a single instance.
        """
        # Encode instance
        input_ids, token_ids, attention_masks, ans_sc = self._encode_metaQA_instance(
            question, agents_predictions
        )

        # Run model
        logits = self.metaqa_model(input_ids, token_ids, attention_masks, ans_sc).logits
        # Get Probabilities
        probs = torch.nn.functional.softmax(logits, dim=2)
        # Get predictions
        pred_list = self._get_metaqa_predictions(
            probs.detach().numpy(), agents_predictions, k=topk
        )
        return pred_list

    def _encode_metaQA_instance(
        self, question: str, agents_predictions: List[Tuple[str, float]], max_len=512
    ):
        """
        Creates input ids, token ids, token masks for an instance of MetaQA.
        """
        # Create input ids, token ids, and masks
        list_input_ids = []
        list_token_ids = []
        list_attention_masks = []
        list_ans_sc = []

        # Process question
        list_input_ids.extend(
            self.tokenizer.encode("[CLS]", add_special_tokens=False)
        )  # [CLS]
        list_input_ids.extend(
            self.tokenizer.encode(question, add_special_tokens=False)
        )  # Query token ids
        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # [SEP]
        list_token_ids.extend(len(list_input_ids) * [0])
        list_ans_sc.extend(len(list_input_ids) * [0])

        # Process qa_agents predictions
        for qa_agent_pred in agents_predictions:
            list_input_ids.append(1)  # [RANK]
            ans_input_ids = self.tokenizer.encode(
                qa_agent_pred[0], add_special_tokens=False
            )
            list_input_ids.extend(ans_input_ids)
            list_token_ids.extend(
                (len(ans_input_ids) + 1) * [1]
            )  # +1 to account for [RANK]
            ans_score = qa_agent_pred[1]
            list_ans_sc.extend(
                (len(ans_input_ids) + 1) * [ans_score]
            )  # +1 to account for [RANK]

        list_input_ids.extend(
            self.tokenizer.encode("[SEP]", add_special_tokens=False)
        )  # last [SEP]
        list_token_ids.append(1)
        list_ans_sc.append(0)
        list_attention_masks.extend(len(list_input_ids) * [1])

        len_padding = max_len - len(list_input_ids)
        list_input_ids.extend([0] * len_padding)  # [PAD]
        list_token_ids.extend((len(list_input_ids) - len(list_token_ids)) * [1])
        list_ans_sc.extend((len(list_input_ids) - len(list_ans_sc)) * [0])
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
            return list_input_ids, list_token_ids, list_attention_masks, list_ans_sc

    def _get_metaqa_predictions(self, logits, agents_predictions, k):
        top_k = lambda a, k: np.argsort(-a)[:k]
        list_preds = []
        for idx in top_k(logits[0][:, 1], self.metaqa_model.num_agents):
            pred = agents_predictions[idx][0]
            if pred != "":
                agent_idx = idx
                metaqa_score = logits[0][idx][1]
                agent_score = agents_predictions[idx][1]
                list_preds.append((pred, agent_idx, metaqa_score, agent_score))
                if len(list_preds) == k:
                    break
        return list_preds
