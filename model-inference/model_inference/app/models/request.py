from enum import Enum
from typing import List, Optional, Union

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
        "numpy arrays (as lists). For the numpy arrays, also set is_preprocessed=True. "
        "<br><br>"
        "Transformer/ Adapter:<br>"
        "Task 'question_answering' expects the input to be in the (question, context) format.",
    )
    is_preprocessed: bool = Field(
        default=False,
        description="Flag indicating that the input contains already pre-processed numpy arrays "
        "as list and that it needs no further pre-processing.<br><br>"
        "Transformer/ Adapter/ SentenceTransformer: 'is_preprocessed' is not supported.",
    )
    preprocessing_kwargs: dict = Field(
        default={},
        description="Optional dictionary containing additional parameters for the pre-processing step.<br><br>"
        "SentenceTransformer: This is ignored.<br>"
        "Transformer/ Adapter: See the Huggingface tokenizer for possible parameters.",
    )
    model_kwargs: dict = Field(
        default={},
        description="Optional dictionary containing parameters that are passed to the model for the forward pass "
        "to control what additional tensors are returned.<br><br>"
        "SentenceTransformer: This is ignored.<br>"
        "Transformer/ Adapter: See the forward method of the Huggingface models for possible parameters"
        "For example, set ‘output_attentions=True’ to receive the attention results in the output.",
    )
    # task: Task = Field(...)
    task_kwargs: dict = Field(
        default={},
        description="Optional dictionary containing additional parameters for handling of the task and "
        "task-related post-processing.<br><br>"
        "SentenceTransformer: This is ignored.<br>"
        "Transformer/ Adapter:<br>"
        "'sentence_classification':<br>"
        "- 'is_regression': Flag to treat output of models with num_labels>1 as regression, too, i.e., no softmax and no labels are returned<br>"
        "'token_classification':<br>"
        "- 'is_regression': Flag to treat output of models with num_labels>1 as regression, too, i.e., no softmax and no labels are returned<br>"
        "'embedding':<br>"
        "- 'embedding_mode: One of 'mean', 'max', 'cls', 'pooler', 'token'. The pooling mode used (or not used for 'token'). "
        "'pooler' uses the pooler_output of a Transformer, i.e. the processed  CLS token. Default value 'mean'.<br>"
        "'question_answering':<br>"
        "- 'topk': Return the top-k most likely spans. Default 1.<br>"
        "- 'max_answer_len': Maximal token length of answers. Default 128.<br>"
        "'generation':<br>"
        "- 'clean_up_tokenization_spaces': See parameter in Huggingface tokenizer.decode(). Default False<br>"
        "- See Huggingface model.generate() for all possible parameters that can be used. "
         "Note, 'model_kwargs' and 'task_kwargs' are merged for generation.<br>"
        "'normalize',boolen, 'True' for using normalized embedding, default 'False' ",
    )
    explain_kwargs: dict = Field(
        default={},
        description="Optional dictionary containing additional parameters for explaining predictions<br>"
        "- 'method': explanation method such as 'simple_grads, integrated_grads,"
        "smooth_grads, attention or scaled_attention':<br>"
        "- 'top_k': number of word attributions to return:<br>"
        "- 'mode: One of 'question', 'context', 'all'. Returns respective attributions. ",
    )
    attack_kwargs: dict = Field(
        default={},
        description="Optional dictionary containing additional parameters for attacking models<br>"
        "- 'method': explanation method such as 'hotflip', 'input_reduction' <br>"
        " 'saliency_method': simple_grads, integrated_grads, smooth_grads, attention or scaled_attention :<br>"
        "- 'max_flips': number of words to flip in hotflip <br>"
        "- 'include_answer: Whether to remove answer from context while attacking model. ",
    )
    adapter_name: Optional[str] = Field(
        default="",
        description="Only necessary for Adapter. "
        "The fully specified name of the to-be-used adapter from adapterhub.ml",
    )
