from pydantic import BaseModel, Field
from typing import List, Optional

class TopkTokens(BaseModel):
    model_name: str = Field(..., description="name of the model")
    adapter: str = Field(..., description="name of the adapter")
    gradient_way: str = Field(..., description="simple/smooth/integrated")
    question: str = Field(..., description="question")
    context: str = Field(..., description="context")
    topk: int  = Field(..., description="desired number of flips if not needed put 0")