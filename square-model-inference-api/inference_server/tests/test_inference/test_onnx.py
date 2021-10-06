import pytest

import numpy as np

from square_model_inference.models.request import Task


@pytest.mark.usefixtures("test_onnx_sequence_classification")
class TestOnnxSequenceClassification:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                       (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification(self, prediction_request, test_onnx_sequence_classification, input):
        prediction_request.input = input
        prediction_request.task_kwargs["embedding_mode"] = "pooler"

        prediction = await test_onnx_sequence_classification.predict(prediction_request, Task.sequence_classification)
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), [1.0] * len(input),
                                   err_msg="logits are softmax")
        assert len(prediction.labels) == len(input)
        assert all(isinstance(prediction.labels[i], int) for i in range(len(input)))
        assert "logits" in prediction.model_outputs

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                       (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification_regression(self, prediction_request,
                                                      test_onnx_sequence_classification, input):
        prediction_request.input = input
        prediction_request.task_kwargs = {"is_regression": True}

        prediction = await test_onnx_sequence_classification.predict(prediction_request,
                                                                     Task.sequence_classification)
        assert not np.array_equal(np.sum(prediction.model_outputs["logits"], axis=-1) - 1,
                                  [0.0] * len(input)), "logits are not softmax"
        assert "logits" in prediction.model_outputs


@pytest.mark.usefixtures("test_onnx_token_classification")
class TestOnnxTokenClassification:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,word_ids", [(["this is a test"], [[None, 0, 1, 2, 3, None]]),
                                              (["this is a test", "this is a test with a longer sentence"],
                                               [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification(self, prediction_request, test_onnx_token_classification, input, word_ids):
        prediction_request.input = input

        prediction = await test_onnx_token_classification.predict(prediction_request, Task.token_classification)
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), np.ones(shape=(len(input), len(word_ids[0]))), rtol=1e-6, err_msg="logits are softmax")
        assert all(len(prediction.labels[i]) == len(word_ids[i]) for i in range(len(input)))
        assert "logits" in prediction.model_outputs
        assert prediction.word_ids == word_ids


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,word_ids", [(["this is a test"],
                                                        [[None, 0, 1, 2, 3, None]]),
                                                       (["this is a test", "this is a test with a longer sentence"],
                                                        [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification_regression(self, prediction_request, test_onnx_token_classification, input, word_ids):
        prediction_request.input = input
        prediction_request.task_kwargs = {"is_regression": True}

        prediction = await test_onnx_token_classification.predict(prediction_request, Task.token_classification)
        assert not np.array_equal((np.sum(prediction.model_outputs["logits"], axis=-1), np.ones_like(word_ids)), "logits are not softmax")
        assert "logits" in prediction.model_outputs
        assert prediction.word_ids == word_ids

@pytest.mark.usefixtures("test_onnx_embedding")
class TestOnnxEmbedding:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,mode", [(["this is a test"], "mean"),
                                              (["this is a test", "this is a test with a longer sentence"], "mean"),
                                            (["this is a test"], "max"),
                                            (["this is a test", "this is a test with a longer sentence"], "max"),
                                            (["this is a test"], "cls"),
                                            (["this is a test", "this is a test with a longer sentence"], "cls"),
                                            (["this is a test"], "pooler"),
                                            (["this is a test", "this is a test with a longer sentence"], "pooler")],
                             )
    async def test_embedding(self, prediction_request, test_onnx_embedding, input, mode):
        prediction_request.input = input
        prediction_request.task_kwargs = {"embedding_mode": mode}

        prediction = await test_onnx_embedding.predict(prediction_request, Task.embedding)
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)
        assert "hidden_states" not in prediction.model_outputs
        assert prediction.embedding_mode == mode

    @pytest.mark.asyncio
    async def test_embedding_unknown_mode(self, prediction_request, test_onnx_embedding):
        prediction_request.task_kwargs = {"embedding_mode": "this mode does not exist"}

        with pytest.raises(ValueError):
            prediction = await test_onnx_embedding.predict(prediction_request, Task.embedding)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, prediction_request, test_onnx_embedding):
        prediction_request.is_preprocessed = True

        with pytest.raises(ValueError):
            prediction = await test_onnx_embedding.predict(prediction_request, Task.embedding)

    @pytest.mark.asyncio
    async def test_input_too_big(self, prediction_request, test_onnx_embedding):
        prediction_request.input = ["test"]*1000

        with pytest.raises(ValueError):
            prediction = await test_onnx_embedding.predict(prediction_request, Task.embedding)

@pytest.mark.usefixtures("test_onnx_question_answering")
class TestOnnxQuestionAnswering:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [([["What is a test?", "A test is a thing where you test."]]),
                                       ([["What is a test?", "A test is a thing where you test."],
                                         ["What is a longer test?", "A test is a thing where you test. If it is longer you call it longer"]])],
                             )
    async def test_question_answering(self, prediction_request, test_onnx_question_answering, input):
        prediction_request.input = input
        prediction_request.task_kwargs = {"topk": 1}

        prediction = await test_onnx_question_answering.predict(prediction_request, Task.question_answering)
        answers = [input[i][1][prediction.answers[i][0].start:prediction.answers[i][0].end] for i in range(len(input))]
        assert "start_logits" in prediction.model_outputs and "end_logits" in prediction.model_outputs
        assert len(prediction.answers) == len(input)
        assert all(prediction.answers[i][0].answer == answers[i] for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_question_answering_topk(self, prediction_request, test_onnx_question_answering):
        input = [["What is a test?", "A test is a thing where you test."]]
        prediction_request.input = input
        prediction_request.task_kwargs = {"topk": 2}

        prediction = await test_onnx_question_answering.predict(prediction_request, Task.question_answering)
        answers = [input[0][1][prediction.answers[0][i].start:prediction.answers[0][i].end] for i in range(2)]
        assert "start_logits" in prediction.model_outputs and "end_logits" in prediction.model_outputs
        assert len(prediction.answers) == len(input)
        assert prediction.answers[0][0].score >= prediction.answers[0][1].score
        assert all(prediction.answers[0][i].answer == answers[i] for i in range(2))


@pytest.mark.usefixtures("test_onnx_generation")
class TestOnnxGeneration:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["Generate text"]),
                                       (["Generate text", "And a lot more text"])],
                             )
    async def test_generation(self, prediction_request, test_onnx_generation, input):
        prediction_request.input = input

        prediction = await test_onnx_generation.predict(prediction_request, Task.generation)
        assert all(isinstance(prediction.generated_texts[i][0], str) for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_generation_output_attention_and_scores(self, prediction_request, test_onnx_generation):
        prediction_request.model_kwargs = {
            "output_attentions": True,
            "output_scores": True
        }

        prediction = await test_onnx_generation.predict(prediction_request, Task.generation)
        assert "scores" in prediction.model_outputs

    @pytest.mark.skip("No beam search implemented")
    @pytest.mark.asyncio
    async def test_generation_beam_sample_multiple_seqs(self, prediction_request, test_onnx_generation):
        prediction_request.task_kwargs = {
            "num_beams": 2,
            "do_sample": True,
            "top_k": 10,
            "top_p": 0.5,
            "no_repeat_ngram_size": 2,
            "num_return_sequences": 2
        }

        prediction = await test_onnx_generation.predict(prediction_request, Task.generation)
        assert len(prediction.generated_texts[0]) == 2