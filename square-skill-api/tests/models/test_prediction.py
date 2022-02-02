import itertools

import pytest

from square_skill_api.models.prediction import PredictionDocument, QueryOutput, NO_ANSWER_FOUND_STRING


@pytest.mark.parametrize(
    "answer_scores,document_scores",
    (
        ([0.9, 0.8, 0.7], [0.3, 0.4]),
        ([0.7, 0.8, 0.9], [0.4, 0.3]),
        ([0.7, 0.9, 0.8], [None, None, None]),
    ),
)
def test_query_output_autosort(answer_scores, document_scores, predictions_factory):

    predictions = predictions_factory(
        answer_scores=answer_scores, document_scores=document_scores
    )

    query_output = QueryOutput(predictions=predictions)
    assert query_output.predictions[0].prediction_output.output_score == max(
        answer_scores
    )
    assert query_output.predictions[-1].prediction_output.output_score == min(
        answer_scores
    )
    if all(s is not None for s in document_scores):
        assert query_output.predictions[0].prediction_documents[
            0
        ].document_score == max(document_scores)
        assert query_output.predictions[-1].prediction_documents[
            0
        ].document_score == min(document_scores)


@pytest.mark.parametrize(
    "context",
    [None, "document", ["documentA", "documentB"]],
    ids=["context=None", "context=str", "context=List[str]"],
)
def test_query_output_from_sequence_classification(
    context,
    model_api_sequence_classification_ouput_factory,
):
    n = 3
    answers = ["door {i}".format(i=i) for i in range(n)]
    model_api_output = model_api_sequence_classification_ouput_factory(n=n)
    context = None
    query_output = QueryOutput.from_sequence_classification(
        answers=answers, model_api_output=model_api_output, context=context
    )

    if context is None:
        assert all(p.prediction_documents == [] for p in query_output.predictions)
    elif isinstance(context, str):
        assert all(
            p.prediction_documents == [PredictionDocument(document=context)]
            for p in query_output.predictions
        )
    elif isinstance(context, list):
        assert all(
            p.prediction_documents == [PredictionDocument(document=c) for c in context]
            for p in query_output.predictions
        )


@pytest.mark.parametrize(
    "context,context_score,test_no_answer,n",
    [
        (None, None, False, 5),
        ("document", 0.9, False, 5),
        ("document", None, False, 5),
        (["documentA", "documentB"], [0.7, 0.3], False, 5),
        (["documentA", "documentB"], [0.7, 0.9], True, 5),
    ],
    ids=["context=None", "context=str", "context=str,score=None", "context=List[str]", "context=List[str],no-answer"],
)
def test_query_output_from_question_answering(
    context, context_score, test_no_answer, n, model_api_question_answering_ouput_factory
):
    model_api_output = model_api_question_answering_ouput_factory(
        n_docs=len(context) if isinstance(context, list) else 1, n_answers=n
    )
    if test_no_answer:
        model_api_output["answers"][1][-1]["answer"] = NO_ANSWER_FOUND_STRING
    query_output = QueryOutput.from_question_answering(
        model_api_output=model_api_output, context=context, context_score=context_score
    )
    if context is None:
        assert all(p.prediction_documents == [] for p in query_output.predictions)
    elif isinstance(context, str):
        # span=[0, 0] is hardcoded in the model_api_question_answering_ouput_factory
        assert all(
            p.prediction_documents
            == [
                PredictionDocument(
                    document=context,
                    span=[0, 0],
                    document_score=context_score if context_score is not None else 1,
                )
            ]
            for p in query_output.predictions
        ), query_output
    elif isinstance(context, list):
        if test_no_answer:
            assert query_output.predictions[-1].prediction_output.output == NO_ANSWER_FOUND_STRING
        else:
            assert query_output.predictions[0].prediction_documents[0].document_score == max(
                context_score
            )
            assert query_output.predictions[-1].prediction_documents[0].document_score == min(
                context_score
            )
