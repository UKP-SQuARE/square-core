from pydantic import BaseModel
from typing import Optional

class SkillModelAdapter(BaseModel):
    context: str
    base_model: str
    adapter: str

class Query(BaseModel):
    query: str
    skill_args: SkillModelAdapter
    num_results: Optional[int] = None
    user_id: Optional[str] = None 

class Skill(BaseModel):
    skill_id:str
    skill_name:str
    skill_type:str


