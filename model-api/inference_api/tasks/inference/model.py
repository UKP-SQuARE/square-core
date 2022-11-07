from typing import Dict

from tasks.models.prediction import PredictionOutput
from tasks.models.request import Task


class Model:
    """
    Base class for all models.
    __init__ is supposed to load all weights and other necessary files (e.g. tokenizer)
    so that the model can directly perform inference on request
    """

    def predict(self, payload: Dict, task: Task) -> PredictionOutput:
        """
        Take an input, pre-process it accordingly, perform inference according to the task,
        post-process the result and return it

        Args:
             payload: the prediction request containing the input and any other parameters required
             task: The task that the model should perform with the payload
        Returns:
             PredictionOutput: the result of the prediction
        """
        raise NotImplementedError
