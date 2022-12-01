from typing import Dict, List, Tuple

import numpy as np


class Attacker:
    """
    Base Attacker class that all other attack classes inherit from.
    """

    def __init__(self, request, task: str, model_outputs: Dict):
        """
        Initialize the Attacker class.

        Args:
            request (Request): The request object.
            task (str): The task to attack.
            model_outputs (Dict): The model outputs.
        """

        self.task = task
        self.request = request
        self.model_outputs = model_outputs
        self.base_prediction_request = {
            "input": [],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task_kwargs": {},
            "adapter_name": self.request.adapter_name,
        }

    def _get_tokens_and_attributions(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, str, str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        get the tokens and attributions from the model outputs
        """
        attributions = self.model_outputs["attributions"][0]
        question_attributions = attributions["question_tokens"][0]
        context_attributions = attributions["context_tokens"][0]

        question_tokens = np.array([word[1] for word in question_attributions])
        question_scores = np.array([word[2] for word in question_attributions])

        context_tokens = np.array([word[1] for word in context_attributions])
        context_scores = np.array([word[2] for word in context_attributions])

        question_text = " ".join(question_tokens)
        context_text = " ".join(context_tokens)

        return (
            question_attributions,
            context_attributions,
            question_text,
            context_text,
            question_tokens,
            question_scores,
            context_tokens,
            context_scores,
        )

    def attack_instance(self):
        """
        attack the instance
        """
        raise NotImplementedError()

    @staticmethod
    def _prepare_qa_inputs(question_text: List[str], context_text: List[str]):
        """
        prepare the instance

        Args:
            question_text (List[str]): The question text.
            context_text (List[str]): The context text.

        Returns:
            inputs (List): The prepared inputs.
        """
        inputs = [[query, context] for query, context in zip(question_text, context_text)]
        return inputs

    @staticmethod
    def _prepare_categorical_inputs(
        question_text: List[str],
        context_text: List[str],
        choice_text: List[List[str]] = None,
    ):
        """
        prepare the instance

        Args:
            question_text (List[str]): The question text.
            context_text (List[str]): The context text.
            choice_text (List[List[str]]): The choice text.

        Returns:
            inputs (List): The prepared inputs.
        """
        if question_text and context_text and choice_text is None:
            inputs = [[context, query] for query, context in zip(question_text, context_text)]
        elif context_text is None and choice_text:
            inputs = [[[query, choice] for choice in choices] for query, choices in zip(question_text, choice_text)]
        else:
            inputs = [
                [[context, query + " " + choice] for choice in choices]
                for query, context, choices in zip(question_text, context_text, choice_text)
            ]
        return inputs

    def prepare_data(
        self,
        question_text: List[str],
        context_text: List[str],
        choice_text: List[List[str]] = None,
    ):
        """
        prepare the instance

        Args:
            question_text (List[str]): The question text.
            context_text (List[str]): The context text.
            choice_text (List[List[str]]): The choice text.

        Returns:
            inputs (List): The prepared inputs based on the task.
        """
        if self.task == "question_answering":
            inputs = self._prepare_qa_inputs(question_text, context_text)
        elif self.task == "sequence_classification":
            inputs = self._prepare_categorical_inputs(question_text, context_text, choice_text)
        else:
            raise ValueError(f"Unknown task {self.task}")
        return inputs
