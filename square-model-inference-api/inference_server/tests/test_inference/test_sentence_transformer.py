import pytest

import numpy as np

from square_model_inference.models.request import Task


@pytest.mark.usefixtures("test_sentence_transformer")
class TestSentenceTransformerEmbedding:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                            (["this is a test", "this is a test with a longer sentence"])])
    async def test_embedding(self, prediction_request, test_sentence_transformer, input):
        prediction_request.input = input

        prediction = await test_sentence_transformer.predict(prediction_request, Task.embedding)
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)

    @pytest.mark.asyncio
    async def test_not_embedding(self, prediction_request, test_sentence_transformer):
        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(prediction_request, Task.sequence_classification)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, prediction_request, test_sentence_transformer):
        prediction_request.is_preprocessed = True

        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(prediction_request, Task.embedding)

    @pytest.mark.asyncio
    async def test_input_too_big(self, prediction_request, test_sentence_transformer):
        prediction_request.input = ["test"]*1000

        with pytest.raises(ValueError):
            prediction = await test_sentence_transformer.predict(prediction_request, Task.embedding)