import pytest

import numpy as np


@pytest.mark.usefixtures("test_sentence_transformer")
class TestSentenceTransformerEmbedding:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                            (["this is a test", "this is a test with a longer sentence"])])
    async def test_embedding(self, prediction_request, test_sentence_transformer, input):
        prediction_request.task = "embedding"
        prediction_request.input = input

        prediction = await test_sentence_transformer.predict(prediction_request)
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)

    @pytest.mark.asyncio
    async def test_not_embedding(self, prediction_request, test_sentence_transformer):
        prediction_request.task = "sequence_classification"
        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(prediction_request)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, prediction_request, test_sentence_transformer):
        prediction_request.task = "embedding"
        prediction_request.is_preprocessed = True

        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(prediction_request)