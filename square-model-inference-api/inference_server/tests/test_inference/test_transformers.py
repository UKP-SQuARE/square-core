import pytest

from square_model_inference.models.request import PredictionRequest
import numpy as np

@pytest.mark.usefixtures("test_transformer_sequence_classification")
class TestTransformerSequenceClassification:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]),
                                              (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification(self, test_transformer_sequence_classification, input):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "sequence_classification",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_transformer_sequence_classification.predict(request)
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), [1.0]*len(input), err_msg="logits are softmax")
        assert len(prediction.task_outputs["labels"]) == len(input)
        assert all(isinstance(prediction.task_outputs["labels"][i], int) for i in range(len(input)))
        assert "logits" in prediction.model_outputs
        assert "id2label" in prediction.task_outputs

    @pytest.mark.asyncio
    async def test_sequence_classification_output_attention(self, test_transformer_sequence_classification):
        request = PredictionRequest.parse_obj({
            "input": ["testing test"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {"output_attentions": True},
            "task": "sequence_classification",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_transformer_sequence_classification.predict(request)
        assert "attentions" in prediction.model_outputs

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [(["this is a test"]), 
                                       (["this is a test", "this is a test with a longer sentence"])],
                             ids=["single", "batch"])
    async def test_sequence_classification_regression(self, test_transformer_sequence_classification, input):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "sequence_classification",
            "task_kwargs": {"is_regression": True},
            "adapter_name": ""
        })

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
    async def test_token_classification(self, test_transformer_token_classification, input, word_ids):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "token_classification",
            "task_kwargs": {},
            "adapter_name": ""
        })

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
    async def test_token_classification_regression(self, test_transformer_token_classification, input, word_ids):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "token_classification",
            "task_kwargs": {"is_regression": True},
            "adapter_name": ""
        })

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
    async def test_embedding(self, test_transformer_embedding, input, mode):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {"embedding_mode": mode},
            "adapter_name": ""
        })

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
    async def test_embedding_token(self, test_transformer_embedding, input, word_ids):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {"embedding_mode": "token"},
            "adapter_name": ""
        })

        prediction = await test_transformer_embedding.predict(request)
        assert np.array(prediction.model_outputs["embeddings"]).shape[2] == 768
        assert np.array(prediction.model_outputs["embeddings"]).shape[1] == len(word_ids[0])
        assert np.array(prediction.model_outputs["embeddings"]).shape[0] == len(input)
        assert "hidden_states" not in prediction.model_outputs
        assert prediction.task_outputs["embedding_mode"] == "token"
        assert prediction.task_outputs["word_ids"] == word_ids

    @pytest.mark.asyncio
    async def test_embedding_unknown_mode(self, test_transformer_embedding):
        request = PredictionRequest.parse_obj({
            "input": ["test"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "embedding",
            "task_kwargs": {"embedding_mode": "this mode does not exist"},
            "adapter_name": ""
        })
        with pytest.raises(ValueError):
            prediction = await test_transformer_embedding.predict(request)

    @pytest.mark.asyncio
    async def test_forbid_is_preprocessed(self, test_transformer_embedding):
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
            prediction = await test_transformer_embedding.predict(request)

@pytest.mark.usefixtures("test_transformer_question_answering")
class TestTransformerQuestionAnswering:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input", [([["What is a test?", "A test is a thing where you test."]]),
                                       ([["What is a test?", "A test is a thing where you test."],
                                         ["What is a longer test?", "A test is a thing where you test. If it is longer you call it longer"]])],
                             )
    async def test_question_answering(self, test_transformer_question_answering, input):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "question_answering",
            "task_kwargs": {"topk": 1},
            "adapter_name": ""
        })

        prediction = await test_transformer_question_answering.predict(request)
        answers = [input[i][1][prediction.task_outputs["answers"][i][0]["start"]:prediction.task_outputs["answers"][i][0]["end"]] for i in range(len(input))]
        assert "start_logits" in prediction.model_outputs and "end_logits" in prediction.model_outputs
        assert len(prediction.task_outputs["answers"]) == len(input)
        assert all(prediction.task_outputs["answers"][i][0]["answer"] == answers[i] for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_question_answering_topk(self, test_transformer_question_answering):
        input = [["What is a test?", "A test is a thing where you test."]]
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "question_answering",
            "task_kwargs": {"topk": 2},
            "adapter_name": ""
        })

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
    async def test_generation(self, test_transformer_generation, input):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "generation",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_transformer_generation.predict(request)
        assert all(isinstance(prediction.task_outputs["generated_texts"][i][0], str) for i in range(len(input)))

    @pytest.mark.asyncio
    async def test_generation_output_attention_and_scores(self, test_transformer_generation):
        request = PredictionRequest.parse_obj({
            "input": ["Generate text"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {
                "output_attentions": True,
                "output_scores": True
            },
            "task": "generation",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_transformer_generation.predict(request)
        assert "scores" in prediction.model_outputs
        assert "attentions" in prediction.model_outputs

    @pytest.mark.asyncio
    async def test_generation_beam_sample_multiple_seqs(self, test_transformer_generation):
        request = PredictionRequest.parse_obj({
            "input": ["Generate text"],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "generation",
            "task_kwargs": {
                "num_beams": 2,
                "do_sample": True,
                "top_k": 10,
                "top_p": 0.5,
                "no_repeat_ngram_size": 2,
                "num_return_sequences": 2
            },
            "adapter_name": ""
        })

        prediction = await test_transformer_generation.predict(request)
        assert len(prediction.task_outputs["generated_texts"][0]) == 2