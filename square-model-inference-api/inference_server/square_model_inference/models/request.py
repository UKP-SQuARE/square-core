from enum import Enum
from typing import Union, List, Optional

from pydantic import BaseModel, Field


class Task(str, Enum):
    """
    The available tasks that can be handled. Note that most model actually supports only one task.
    Requesting a task that a model cannot handle might fail or produce incorrect results.
    """
    sequence_classification = "sequence_classification"
    token_classification = "token_classification"
    question_answering = "question_answering"
    embedding = "embedding"
    generation = "generation"


class PredictionRequest(BaseModel):
    """
    Prediction request containing the input, pre-processing parameters, parameters for the model forward pass,
     the task with task-specific parameters, and parameters for any post-processing
    """
    input: Union[List[str], List[List[str]], dict] = Field(
        ...,
        description="Input for the model. Supports Huggingface Transformer inputs (i.e., list of sentences, or "
                    "list of pairs of sentences), a dictionary with Transformer inputs, or a dictionary containing "
                    "numpy arrays (as lists). For the numpy arrays, also set is_preprocessed=True."
    )
    is_preprocessed: bool = Field(
        default=False,
        description="Flag indicating that the input contains already pre-processed numpy arrays "
                    "as list and that it needs no further pre-processing."
    )
    preprocessing_kwargs: dict = Field(
        default={},
        description="Dictionary containing additional parameters for the pre-processing step."
    )
    model_kwargs: dict = Field(
        default={},
        description="Dictionary containing parameters that are passed to the model for the forward pass. "
                    "Set ‘output_attention=True’ to receive the attention weights for Huggingface Transformers in the "
                    "output."
    )
    task: Task = Field(...)
    task_kwargs: dict = Field(
        default={},
        description="Dictionary containing additional parameters for handling of the task and "
                    "task-related post-processing."
    )
    adapter_name: Optional[str] = Field(
        default="",
        description="Only necessary for adapter-based models. "
                    "The fully specified name of the to-be-used adapter from adapterhub.ml"
    )