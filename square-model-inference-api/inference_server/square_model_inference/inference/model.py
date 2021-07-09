from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.models.prediction import PredictionOutput


class Model:
    """
    Base class for all models.
    __init__ is supposed to load all weights and other necessary files (e.g. tokenizer)
    so that the model can directly perform inference on request
    """
    async def predict(self, payload: PredictionRequest, task: Task) -> PredictionOutput:
        """
        Take an input, pre-process it accordingly, perform inference according to the task,
        post-process the result and return it
        :param payload: the prediction request containing the input and any other parameters required
        :param task: The task that the model should perform with the payload
        :return: the result of the prediction
        """
        raise NotImplementedError
