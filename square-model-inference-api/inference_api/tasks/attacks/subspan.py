import logging
from typing import Dict, List, Tuple

from tasks.attacks.attack import Attacker

logger = logging.getLogger(__name__)


class SubSpan(Attacker):
    """
    Selects sub-span with the highest attribution scores
    """

    def __init__(self, task, request, model_outputs):
        """
        Initialize the input reduction attack

        Args:
            request (dict): the request to the model
            task (Task): the task to attack
            model_outputs (dict): the model outputs
        """
        super().__init__(request, task, model_outputs)
        self.top_k = self.request.attack_kwargs.get("max_tokens", 10)

    def attack_instance(self) -> Tuple[List[List], List]:
        """
        selects sub-span with the highest attribution scores
         from the context

        Returns:
            Tuple of reduced span inputs and the span indices
        """

        (
            question_attributions,
            context_attributions,
            question_text,
            context_text,
            _,
            _,
            context_tokens,
            context_scores,
        ) = self._get_tokens_and_attributions()

        # take full context if top_k is greater than the context length
        if self.top_k > len(context_tokens):
            self.top_k = len(context_tokens)

        window = self.top_k
        # select the window with the highest scores
        high = 0
        start_span, end_span = 0, 0
        for i in range(len(context_scores) - window + 1):
            step = i + window
            temp = sum(context_scores[i:step])
            if temp > high:
                high = temp
                start_span = i
                end_span = step
        span_indices = list(range(start_span, end_span))
        reduced_context = [" ".join(context_tokens[start_span:end_span])]
        prepared_inputs = [
            [q, c]
            for q, c in zip(
                [question_text] * (len(reduced_context) + 1),
                [context_text] + reduced_context,
            )
        ]
        batch_request = self.base_prediction_request
        batch_request["input"] = prepared_inputs
        saliency_method = self.request.attack_kwargs.get("saliency_method", "attention")
        if saliency_method in ["attention", "scaled_attention"]:
            batch_request["model_kwargs"] = {"output_attentions": True}
        batch_request["contexts"] = [context_text] + reduced_context
        return batch_request, span_indices
