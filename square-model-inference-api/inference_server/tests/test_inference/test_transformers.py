import pytest

from square_model_inference.models.request import PredictionRequest
import numpy as np

@pytest.mark.usefixtures("test_transformer_sequence_classification")
class TestTransformerSequenceClassification:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                              (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification(self, request, test_transformer_sequence_classification, input):
        request.input = input
        request.task = "sequence_classification"

        prediction = await test_transformer_sequence_classification.predict(request)
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), [1.0]*len(input), err_msg="logits are softmax")
        assert len(prediction.task_outputs["labels"]) == len(input)
        assert all(isinstance(prediction.task_outputs["labels"][i], int) for i in range(len(input)))
        assert "logits" in prediction.model_outputs
        assert "id2label" in prediction.task_outputs

    @pytest.mark.asyncio
    async def test_sequence_classification_output_attention(self, request, test_transformer_sequence_classification):
        request.task = "sequence_classification"
        request.model_kwargs = {"output_attentions": True}

        prediction = await test_transformer_sequence_classification.predict(request)
        assert "attentions" in prediction.model_outputs

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]), 
                                       (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification_regression(self, request, test_transformer_sequence_classification, input):
        request.input = input
        request.task = "sequence_classification"
        request.task_kwargs = {"is_regression": True}

        prediction = await test_transformer_sequence_classification.predict(request)
        assert not np.array_equal(np.sum(prediction.model_outputs["logits"], axis=-1)-1, [0.0]*len(input)), "logits are not softmax"
        assert "labels" not in prediction.task_outputs
        assert "logits" in prediction.model_outputs


@pytest.mark.usefixtures("test_transformer_token_classification")
class TestTransformerTokenClassification:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,word_ids", [(["this is a test"], [[None, 0, 1, 2, 3, None]]),
                                              (["this is a test", "this is a test with a longer sentence"],
                                               [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification(self, request, test_transformer_token_classification, input, word_ids):
        request.input = input
        request.task = "token_classification"

        prediction = await test_transformer_token_classification.predict(request)
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), np.ones(shape=(len(input), len(word_ids[0]))), err_msg="logits are softmax")
        assert all(len(prediction.task_outputs["labels"][i]) == len(word_ids[i]) for i in range(len(input)))
        assert "logits" in prediction.model_outputs
        assert "id2label" in prediction.task_outputs
        assert prediction.task_outputs["word_ids"] == word_ids


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,word_ids", [(["this is a test"],
                                                        [[None, 0, 1, 2, 3, None]]),
                                                       (["this is a test", "this is a test with a longer sentence"],
                                                        [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification_regression(self, request, test_transformer_token_classification, input, word_ids):
        request.input = input
        request.task = "token_classification"
        request.task_kwargs = {"is_regression": True}

        prediction = await test_transformer_token_classification.predict(request)
        assert not np.array_equal((np.sum(prediction.model_outputs["logits"], axis=-1), np.ones_like(word_ids)), "logits are not softmax")
        assert "labels" not in prediction.task_outputs
        assert "logits" in prediction.model_outputs
        assert prediction.task_outputs["word_ids"] == word_ids


@pytest.mark.usefixtures("test_transformer_embedding")
class TestTransformerEmbedding:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,mode", [(["this is a test"], "mean"),
                                              (["this is a test", "this is a test with a longer sentence"], "mean"),
                                            (["this is a test"], "max"),
                                            (["this is a test", "this is a test with a longer sentence"], "max"),
                                            (["this is a test"], "cls"),
                                            (["this is a test", "this is a test with a longer sentence"], "cls")],
                             )
    async def test_embedding(self, request, test_transformer_embedding, input, mode):
        request.input = input
        request.task = "embedding"
        request.task_kwargs = {"embedding_mode": mode}

        prediction = await test_transformer_embedding.predict(request)
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)
        assert "hidden_states" not in prediction.model_outputs
        assert prediction.task_outputs["embedding_mode"] == mode

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,word_ids", [(["this is a test"], [[None, 0, 1, 2, 3, None]]),
                                            (["this is a test", "this is a test with a longer sentence"],
                                             [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_embedding_token(self, request, test_transformer_embedding, input, word_ids):
        request.input = input
        request.task = "embedding"
        request.task_kwargs = {"embedding_mode": "token"}

        prediction = await test_transformer_embedding.predict(request)
        assert np.array(prediction.model_outputs["embeddings"]).shape[2] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == len(word_ids[0])
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)
        assert "hidden_states" not in prediction.model_outputs
        assert prediction.task_outputs["embedding_mode"] == "token"
        assert prediction.task_outputs["word_ids"] == word_ids

    @pytest.mark.asyncio
    async def test_embedding_unknown_mode(self, request, test_transformer_embedding):
        request.task = "embedding"
        request.task_kwargs = {"embedding_mode": "this mode does not exist"}

        with pytest.raises(ValueError):
            prediction = await test_transformer_embedding.predict(request)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, request, test_transformer_embedding):
        request.task = "embedding"
        request.is_preprocessed = True

        with pytest.raises(ValueError):
            prediction = await test_transformer_embedding.predict(request)

@pytest.mark.usefixtures("test_transformer_question_answering")
class TestTransformerQuestionAnswering:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [([["What is a test?", "A test is a thing where you test."]]),
                                       ([["What is a test?", "A test is a thing where you test."],
                                         ["What is a longer test?", "A test is a thing where you test. If it is longer you call it longer"]])],
                             )
    async def test_question_answering(self, request, test_transformer_question_answering, input):
        request.input = input
        request.task = "question_answering"
        request.task_kwargs = {"topk": 1}

        prediction = await test_transformer_question_answering.predict(request)
        answers = [input[i][1][prediction.task_outputs["answers"][i][0]["start"]:prediction.task_outputs["answers"][i][0]["end"]] for i in range(len(input))]
        assert "start_logits" in prediction.model_outputs and "end_logits" in prediction.model_outputs
        assert len(prediction.task_outputs["answers"]) == len(input)
        assert all(prediction.task_outputs["answers"][i][0]["answer"] == answers[i] for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_question_answering_topk(self, request, test_transformer_question_answering):
        request.input = [["What is a test?", "A test is a thing where you test."]]
        request.task = "question_answering"
        request.task_kwargs = {"topk": 2}

        prediction = await test_transformer_question_answering.predict(request)
        answers = [input[0][1][prediction.task_outputs["answers"][0][i]["start"]:prediction.task_outputs["answers"][0][i]["end"]] for i in range(2)]
        assert "start_logits" in prediction.model_outputs and "end_logits" in prediction.model_outputs
        assert len(prediction.task_outputs["answers"]) == len(input)
        assert all(prediction.task_outputs["answers"][0][i]["answer"] == answers[i] for i in range(2))


@pytest.mark.usefixtures("test_transformer_generation")
class TestTransformerGeneration:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["Generate text"]),
                                       (["Generate text", "And more text"])],
                             )
    async def test_generation(self, request, test_transformer_generation, input):
        request.input = input
        request.task = "generation"

        prediction = await test_transformer_generation.predict(request)
        assert all(isinstance(prediction.task_outputs["generated_texts"][i][0], str) for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_generation_output_attention_and_scores(self, request, test_transformer_generation):
        request.task = "generation"
        request.model_kwargs = {
            "output_attentions": True,
            "output_scores": True
        }

        prediction = await test_transformer_generation.predict(request)
        assert "scores" in prediction.model_outputs
        assert "attentions" in prediction.model_outputs

    @pytest.mark.asyncio
    async def test_generation_beam_sample_multiple_seqs(self, request, test_transformer_generation):
        request.task = "generation"
        request.task_kwargs =  {
            "num_beams": 2,
            "do_sample": True,
            "top_k": 10,
            "top_p": 0.5,
            "no_repeat_ngram_size": 2,
            "num_return_sequences": 2
        }

        prediction = await test_transformer_generation.predict(request)
        assert len(prediction.task_outputs["generated_texts"][0]) == 2