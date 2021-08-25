from typing import Dict, Union, Tuple, List, Optional, Iterable
from pydantic import Field, BaseModel


class PredictionOutput(BaseModel):
    output: str = Field(
        ...,
        description="The actual output of the model as string. "
                    "Could be an answer for QA, an argument for AR or a label for Fact Checking."
    )
    output_score: float = Field(
        ...,
        description="The score assigned to the output."
    )


class PredictionDocument(BaseModel):
    index: str = Field("", description="From which document store the document has been retrieved")
    document_id: str = Field("", description="Id of the document in the index")
    document: str = Field(..., description="The text of the document")
    span: Optional[List[int]] = Field(description="Start and end character index of the span used. (optional)")
    url: str = Field("", description="URL source of the document (if available)")
    source: str = Field("", description="The source of the document (if available)")


class Prediction(BaseModel):
    """
    A single prediction for a query.
    """
    prediction_id: str = Field(
        ...,
        description="An identifier for each prediction. This allows to refer to the prediction in other requests."
    )
    prediction_score: float = Field(
        ...,
        description="The overall score assigned to the prediction. Up to the Skill to decide how to calculate"
    )
    prediction_output: PredictionOutput = Field(
        ...,
        description="The prediction output of the skill."
    )
    prediction_documents: List[PredictionDocument] = Field(
        [],
        description="A list of the documents used by the skill to derive this prediction. "
                    "Empty if no documents were used"
    )


class QueryOutput(BaseModel):
    """
    The model for output that the skill returns after processing a query.
    """
    predictions: List[Prediction] = Field(
        ...,
        description="All predictions for the query. Predictions are sorted by prediction_score (descending)"
    )

