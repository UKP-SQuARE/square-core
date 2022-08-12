from typing import List, Dict, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SubSpan:
    def __init__(
        self, top_k,
    ):
        self.top_k = top_k

    def select_span(self, model_outputs) -> Tuple[List[List], List]:
        """
        selects sub-span with the highest attribution scores
         from the context

        Args:
            model_outputs: word importance scores
        Returns:
            Tuple of reduced span inputs and the span indices
        """

        attributions = model_outputs["attributions"][0]
        context_attributions = attributions["context_tokens"][0]
        question_attributions = attributions["question_tokens"][0]

        context_text = " ".join([word[1] for word in context_attributions])
        question_text = " ".join([word[1] for word in question_attributions])

        context_tokens = np.array([word[1] for word in context_attributions])
        context_attr = np.array([word[2] for word in context_attributions])

        # take full context if top_k is greater than the context length
        if self.top_k > len(context_tokens):
            self.top_k = len(context_tokens)

        window = self.top_k
        # select the window with the highest scores
        high = 0
        start_span, end_span = 0, 0
        for i in range(len(context_attr) - window + 1):
            step = i + window
            temp = sum(context_attr[i:step])
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
        logger.info(prepared_inputs)
        return prepared_inputs, span_indices
