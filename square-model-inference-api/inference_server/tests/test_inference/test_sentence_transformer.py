import pytest

import numpy as np
from square_model_inference.models.request import PredictionRequest


@pytest.mark.usefixtures("test_sentence_transformer")
class TestSentenceTransformerEmbedding:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                            (["this is a test", "this is a test with a longer sentence"])])
    async def test_embedding(self, test_sentence_transformer, input):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_sentence_transformer.predict(request)
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)

    @pytest.mark.asyncio
    async def test_not_embedding(self, test_sentence_transformer):
        request = PredictionRequest.parse_obj({
            "input": ["input"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "sequence_classification",
            "task_kwargs": {},
            "adapter_name": ""
        })
        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(request)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, test_sentence_transformer):
        request = PredictionRequest.parse_obj({
            "input": ["test"],
            "is_preprocessed": True,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {},
            "adapter_name": ""
        })
        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(request)