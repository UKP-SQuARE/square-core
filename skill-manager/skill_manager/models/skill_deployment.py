from typing import Optional

from pydantic import BaseModel, Field


class SkillDeployment(BaseModel):
    skill_template_id: str = Field()
    deployed: bool = Field()
    url: Optional[str] = Field()
