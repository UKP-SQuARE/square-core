from pydantic import BaseModel
from typing import Optional

class Skill(BaseModel):
    #path for the query request of the skill
    skill_query_path : str
    #type of the skill : multiple choice, extractive, abstractive etc.
    skill_type : str
    #name of the language model
    skill_base_model : str
    #name of the adapter
    skill_adapter : str
    #id of the skill
    skill_id : str


