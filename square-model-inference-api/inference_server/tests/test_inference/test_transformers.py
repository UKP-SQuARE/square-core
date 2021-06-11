import pytest

from square_model_inference.models.request import PredictionRequest
import numpy as np

@pytest.mark.usefixtures("test_transformer_sequence_classification")
class TestTransformerSequenceClassification:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,output", [(["this is a test"], [1]),
                                              (["this is a test", "this is a test with a longer sentence"], [1, 1])],
                             ids=["single", "batch"])
    async def test_sequence_classification(self, test_transformer_sequence_classification, input, output):
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
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), [1.0]*len(input), err_msg="logits are not converted to softmax")
        assert prediction.task_outputs["labels"] == output
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
    @pytest.mark.parametrize("input,output", [(["this is a test"], [[0.17748619616031647, 0.4802907109260559]]),
                                              (["this is a test", "this is a test with a longer sentence"],
                                               [[0.17748622596263885, 0.48029083013534546], [-0.048022523522377014, 0.5764690637588501]])],
                             ids=["single", "batch"])
    async def test_sequence_classification_regression(self, test_transformer_sequence_classification, input, output):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "sequence_classification",
            "task_kwargs": {"regression": True},
            "adapter_name": ""
        })

        prediction = await test_transformer_sequence_classification.predict(request)
        assert prediction.model_outputs["logits"] == output
        assert "labels" not in prediction.task_outputs
        assert "logits" in prediction.model_outputs


@pytest.mark.usefixtures("test_transformer_token_classification")
class TestTransformerTokenClassification:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,output,word_ids", [(["this is a test"], [[0, 1, 1, 1, 1, 1]], [[None, 0, 1, 2, 3, None]]),
                                              (["this is a test", "this is a test with a longer sentence"],
                                               [[0, 1, 1, 1, 1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
                                               [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification(self, test_transformer_token_classification, input, output, word_ids):
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
        np.testing.assert_allclose(np.sum(prediction.model_outputs["logits"], axis=-1), np.ones_like(output), err_msg="logits are not converted to softmax")
        assert prediction.task_outputs["labels"] == output
        assert "logits" in prediction.model_outputs
        assert "id2label" in prediction.task_outputs
        assert prediction.task_outputs["word_ids"] == word_ids


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input,output,word_ids", [(["this is a test"], [[[0.11221601068973541, 0.05969493091106415],
                                                                              [-0.15642595291137695, -0.07739989459514618],
                                                                              [-0.2801300287246704, 0.06872765719890594],
                                                                              [-0.28268659114837646, -0.01801353693008423],
                                                                              [0.032697953283786774, 0.051608189940452576],
                                                                              [0.01579795777797699, 0.23798659443855286]]],
                                                        [[None, 0, 1, 2, 3, None]]),
                                                       (["this is a test", "this is a test with a longer sentence"],
                                                        [[[0.11221593618392944, 0.059694863855838776],
                                                          [-0.15642589330673218, -0.07740016281604767],
                                                          [-0.2801305651664734, 0.06872743368148804],
                                                          [-0.28268682956695557, -0.018013179302215576],
                                                          [0.03269825875759125, 0.051608070731163025],
                                                          [0.01579788327217102, 0.2379867136478424],
                                                          [0.03173816204071045, -0.15285855531692505],
                                                          [0.11003853380680084, -0.12873490154743195],
                                                          [0.13318589329719543, -0.10646772384643555],
                                                          [0.13220593333244324, -0.12443935126066208]],
                                                         [[-0.05789753794670105, 0.04508095979690552],
                                                          [-0.27872341871261597, -0.1229611188173294],
                                                          [-0.5753417015075684, 0.07893967628479004],
                                                          [-0.47106701135635376, -0.04298338294029236],
                                                          [-0.5324697494506836, 0.10730768740177155],
                                                          [-0.31086403131484985, 0.3265591263771057],
                                                          [-0.2457294911146164, 0.24867495894432068],
                                                          [-0.2389427125453949, 0.4464331567287445],
                                                          [-0.08393016457557678, -0.03680300712585449],
                                                          [-0.01722254604101181, 0.41447973251342773]]],
                                                        [[None, 0, 1, 2, 3, None, None, None, None, None], [None, 0, 1, 2, 3, 4, 5, 6, 7, None]])],
                             ids=["single", "batch"])
    async def test_token_classification_regression(self, test_transformer_token_classification, input, output, word_ids):
        request = PredictionRequest.parse_obj({
            "input": input,
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "token_classification",
            "task_kwargs": {"regression": True},
            "adapter_name": ""
        })

        prediction = await test_transformer_token_classification.predict(request)
        assert prediction.model_outputs["logits"] == output
        assert "labels" not in prediction.task_outputs
        assert "logits" in prediction.model_outputs
        assert prediction.task_outputs["word_ids"] == word_ids


@pytest.mark.usefixtures("test_transformer_embedding")
class TestTransformerSequenceClassification:

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


@pytest.mark.usefixtures("test_transformer_question_answering")
class TestTransformerSequenceClassification:

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
    async def test_generation(self, test_transformer_generation):
        request = PredictionRequest.parse_obj({
            "input": [
                "this is a test"
            ],
            "is_preprocessed": False,
            "preprocessing_kwargs": {},
            "model_kwargs": {},
            "task": "generation",
            "task_kwargs": {},
            "adapter_name": ""
        })

        prediction = await test_transformer_generation.predict(request)
        assert prediction