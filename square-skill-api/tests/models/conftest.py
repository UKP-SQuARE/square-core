import random
from typing import List

from pytest import fixture
from square_skill_api.models import prediction
from square_skill_api.models.prediction import (
    Prediction,
    PredictionDocument,
    PredictionOutput,
)


@fixture
def predictions_factory():
    def generate_predictions(
        answer_scores: List[float],
        document_scores: List[float],
        answers: List[str] = None,
    ):
        predictions = []
        for document_i, document_score in enumerate(document_scores):
            for answer_i, answer_score in enumerate(answer_scores):
                predictions.append(
                    Prediction(
                        prediction_score=answer_score,
                        prediction_output=PredictionOutput(
                            output=answers[answer_i]
                            if answers
                            else f"answer {answer_i}",
                            output_score=answer_score,
                        ),
                        prediction_documents=[
                            PredictionDocument(
                                document=f"document {document_i}",
                                document_score=document_score,
                            )
                            if document_score is not None
                            else PredictionDocument(
                                document="document {document_i}",
                            )
                        ],
                    )
                )
        return predictions

    return generate_predictions


@fixture
def model_api_sequence_classification_ouput_factory():
    def model_api_sequence_classification_ouput(n: int):
        logits = [random.random() for _ in range(n)]
        max_logit = max(logits)
        argmax = logits.index(max_logit)
        return {
            "labels": [argmax],
            "id2label": {i: str(i) for i in range(n)},
            "model_outputs": {
                "logits": [logits],
            },
            "model_output_is_encoded": False,
        }

    return model_api_sequence_classification_ouput


@fixture
def model_api_question_answering_ouput_factory():
    def model_api_question_answering_ouput(
        n_docs: int, n_answers: int, answer: str = None
    ):
        return {
            "answers": [
                [
                    {
                        "score": answer_i / sum(range(n_answers)),
                        "start": 0,
                        "end": 0,
                        "answer": "answer {answer_i} for doc {doc_i}".format(
                            answer_i=str(answer_i), doc_i=str(doc_i)
                        )
                        if answer is None
                        else answer,
                    }
                    for answer_i in range(n_answers)
                ]
                for doc_i in range(n_docs)
            ],
            "model_outputs": {
                "start_logits": "something encoded",
                "end_logits": "something encoded",
            },
            "model_output_is_encoded": True,
        }

    return model_api_question_answering_ouput
