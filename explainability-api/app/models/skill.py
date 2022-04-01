from pydantic import BaseModel, Field

class Skill(BaseModel):
    skill_query_path: str = Field(..., description="path for the query request of the skill")
    skill_type: str = Field(..., description="type of the skill : multiple choice, extractive, abstractive etc.")
    skill_base_model: str = Field(..., description="name of the language model")
    skill_adapter: str = Field(..., description="name of the adapter")
    skill_id: str = Field(..., description="id of the skill")
