from pydantic import BaseModel, Field
from typing import List, Optional

class HotFlip(BaseModel):
    model_name: str = Field(..., description="name of the model")
    adapter: str = Field(..., description="name of the adapter")
    gradient_way: str = Field(..., description="simple/smooth/integrated")
    question: str = Field(..., description="question")
    context: str = Field(..., description="context")
    include_answer: str = Field(..., description="true if it is needed to include the tokens of the answer")
    number_of_flips: int  = Field(..., description="desired number of flips if not needed put 0")