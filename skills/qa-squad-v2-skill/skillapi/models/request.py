from typing import Dict, Any

from pydantic import BaseModel, Field, PositiveInt


class QueryRequest(BaseModel):
    """
    The model for a query request that the skill receives.
    """
    query: str = Field(
        ...,
        description="The input to the model that is entered by the user"
    )
    skill_args: Dict[str, Any] = Field(
        {},
        description="Optional values for specific parameters of the skill"
    )
    num_results: PositiveInt = Field(
        1,
        description="The (max.) number of results to return"
    )
    user_id: str = Field(
        ""
    )
