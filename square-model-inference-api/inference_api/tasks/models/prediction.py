import base64
from io import BytesIO
from typing import Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import torch
from pydantic import BaseModel, Field
from tasks.config.model_config import model_config


def _encode_numpy(
    obj: Dict[str, Union[torch.Tensor, Tuple[torch.Tensor]]],
    return_plaintext: bool = None,
) -> Dict[str, Union[list, str]]:
    """
    Encodes the Torch Tensors first to Numpy arrays and then encodes them either as plain lists or base64 string
    depending on the flag RETURN_PLAINTEXT_ARRAYS
    :param obj: the objects whose tensors will be encoded
    :return: the same dictionary with all tensors replaced by lists or base64-encoded array strings.
    """
    if return_plaintext is None:
        return_plaintext = model_config.return_plaintext_arrays

    # Encode numpy array either as lists or base64 string
    def encode(arr):
        if isinstance(arr, torch.Tensor):
            arr = arr.numpy()
        if return_plaintext:
            return arr.tolist()
        else:
            # np.save expects a file which we emulate with BytesIO
            with BytesIO() as b:
                np.save(b, arr)
                arr_binary = b.getvalue()
            arr_binary_b64 = base64.b64encode(arr_binary)
            arr_string_b64 = arr_binary_b64.decode("latin1")
            return arr_string_b64

            # DECODE THE VALUE WITH
            # arr_binary_b64 = arr_string_b64.encode()
            # arr_binary = base64.decodebytes(arr_binary_b64)
            # arr = np.load(BytesIO(arr_binary))

    # Recursively go through a value and encode leaves (=tensors) it or iterate over values and encode them
    def enc_or_iterate(val):
        # Stop attempt to encode an already encoded array
        # This can happen because PredictionOutput is initialized twice
        # - once by Model and once when request response is serialized by fastAPI
        if isinstance(val, int) or isinstance(val, float) or isinstance(val, str):
            raise ValueError("Array is already encoded")
        if (
            isinstance(val, Iterable)
            and not isinstance(val, torch.Tensor)
            and not isinstance(val, np.ndarray)
        ):
            return [enc_or_iterate(v) for v in val]
        else:
            return encode(val)

    for k, v in obj.items():
        try:
            v = enc_or_iterate(v)
        except ValueError:
            break
        obj[k] = v
    return obj


class PredictionOutput(BaseModel):
    """
    The results of the prediction of the model on the given input for the requested task.
    """

    model_outputs: Dict = Field(
        {},
        description="Dictionary containing the model tensor outputs either as plain list or as base64-encoded numpy array.<br><br>"
        "Decode the base64 string 'arr_string_b64' back to an array in Python like this:<br>"
        "arr_binary_b64 = arr_string_b64.encode()<br>"
        "arr_binary = base64.decodebytes(arr_binary_b64)<br>"
        "arr = np.load(BytesIO(arr_binary))<br><br>"
        "SentenceTransformer:<br>"
        "'embedding':<br>"
        "- 'embeddings: Embedding tensors.<br>"
        "Transformer/ Adapter:<br>"
        "Optional tensor depend on request's 'model_kwargs' parameters, e.g. 'output_attentions'. "
        "See the Huggingface documentation for information like shape etc. <br>"
        "'sentence_classification':<br>"
        "- 'logits': (Softmax) logits of the classifier.<br>"
        "'token_classification':<br>"
        "- 'logits': (Softmax) logits of the classifier.<br>"
        "'embedding':<br>"
        "- 'embeddings: Embedding tensors.<br>"
        "'question_answering':<br>"
        "- 'start_logits': Logits for the beginning of the span<br>"
        "- 'end_logits': Logits for the end of the span<br>"
        "'generation':<br>"
        "- 'sequences': The generated vocab ids for the sequence<br>"
        "Task 'generation' does not concatenate the tensors of the inputs together but instead creates a list"
        "of the tensors for each input.",
    )
    model_output_is_encoded: bool = Field(
        not model_config.return_plaintext_arrays,
        description="Flag indicating that 'model_output' is a base64-encoded numpy array and not a human-readable list."
        "See the field description for 'model_output' on information on how to decode the array.",
    )

    def __init__(self, **data):
        """
        Data model for the model and task outputs.
        The model outputs (,i.e., tensors) will be encoded as base64 strings or as plain lists depending on the flag
        RETURN_PLAINTEXT_ARRAYS.
        :param data:
        'model_outputs': dict[str: Union[torch.Tensor, Tuple[torch.Tensor]]]. All tensor results of the model
        'task_outputs': dict[str: Any]. All non-tensor results of the processed task like the predicted labels,
                        extracted spans, etc.
        """
        super().__init__(**data)
        self.model_outputs = _encode_numpy(self.model_outputs)
        self.model_output_is_encoded = not model_config.return_plaintext_arrays


class TokenAttributions(BaseModel):
    """
    A span answer for question_answering with a score, the start and end character index and the extracted span answer.
    """

    topk_question_idx: List
    topk_context_idx: List
    question_tokens: List[List[Tuple[int, str, float]]]
    context_tokens: List[List[Tuple[int, str, float]]]


class PredictionOutputForSequenceClassification(PredictionOutput):
    labels: List[int] = Field(
        default=[],
        description="List of the predicted label ids for the input. "
        "Not set for regression.",
    )
    id2label: Dict[int, str] = Field(
        default={},
        description="Mapping from label id to the label name. "
        "Not set for regression.",
    )
    attributions: Optional[List[TokenAttributions]] = Field(
        default=[],
        description="scores for the input tokens which are important for the"
        "model prediction",
    )
    questions: Optional[List] = Field(
        default=[], description="The new questions after modification"
    )
    contexts: Optional[List] = Field(
        default=[], description="The new contexts after modification"
    )
    adversarial: Optional[Dict] = Field(
        default={},
        description="scores for the input tokens which are important for the"
        "model prediction",
    )

    def __init__(self, **data):
        super().__init__(**data)


class PredictionOutputForGraphSequenceClassification(PredictionOutput):
    labels: List[int] = Field(
        default=[],
        description="List of the predicted label ids for the input. "
        "Not set for regression.",
    )
    lm_subgraph: Optional[Dict[str, Dict]] = Field(
        default={}, description="return the lm scored subgraph"
    )
    attn_subgraph: Optional[Dict[str, Dict]] = Field(
        default={}, description="return the attention subgraph"
    )

    def __init__(self, **data):
        super().__init__(**data)


class PredictionOutputForTokenClassification(PredictionOutput):
    labels: List[List[int]] = Field(
        [],
        description="List of the predicted label ids for the input. Not set "
        "for regression.",
    )
    id2label: Dict[int, str] = Field(
        {},
        description="Mapping from label id to the label name. Not set for regression.",
    )
    word_ids: List[List[Optional[int]]] = Field(
        ...,
        description="Mapping from each token to the corresponding word "
        "in the input. 'None' represents special tokens "
        "added by tokenizer",
    )

    def __init__(self, **data):
        super().__init__(**data)


class PredictionOutputForEmbedding(PredictionOutput):
    embedding_mode: str = Field(
        "",
        description="Only used by Transformers/ Adapters.<br> One of 'mean', 'max', 'cls', "
        "'pooler', 'token'. The pooling mode used (or not used for 'token')",
    )
    word_ids: List[List[Optional[int]]] = Field(
        [],
        description="Only used by Transformers/ Adapters.<br> "
        "Only set with embedding_mode='token'."
        " Mapping from each token to the corresponding word "
        "in the input. 'None' represents special tokens added "
        "by tokenizer",
    )

    def __init__(self, **data):
        super().__init__(**data)


class PredictionOutputForGeneration(PredictionOutput):
    generated_texts: List[List[str]] = Field(
        ...,
        description="List of list of the generated texts. Length of outer "
        "list is the number of inputs, length of inner list is "
        "parameter 'num_return_sequences' in request's 'task_kwargs'",
    )

    def __init__(self, **data):
        super().__init__(**data)


class QAAnswer(BaseModel):
    """
    A span answer for question_answering with a score, the start and end character index and the extracted span answer.
    """

    score: float
    start: int
    end: int
    answer: str


class PredictionOutputForQuestionAnswering(PredictionOutput):
    answers: List[List[QAAnswer]] = Field(
        ...,
        description="List of lists of answers. Length of outer list is the number "
        "of inputs, length of inner list is parameter 'topk' from the "
        "request's 'task_kwargs' (default 1). Each answer is a "
        "dictionary with 'score', 'start' (span start index in context), "
        "'end' (span end index in context), and 'answer' "
        "(the extracted span). The inner list is sorted by score. If no "
        "answer span was extracted, the empty span is returned "
        "(start and end both 0)",
    )
    questions: Optional[List] = Field(
        [], description="The new questions after modification"
    )
    contexts: Optional[List] = Field(
        [], description="The new contexts after modification"
    )
    attributions: Optional[List[TokenAttributions]] = Field(
        [],
        description="scores for the input tokens which are important for the"
        "model prediction",
    )
    adversarial: Optional[Dict] = Field(
        {},
        description="scores for the input tokens which are important for the"
        "model prediction",
    )

    def __init__(self, **data):
        super().__init__(**data)
