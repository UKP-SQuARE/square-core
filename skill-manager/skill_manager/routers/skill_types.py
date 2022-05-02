import logging
from typing import List

from fastapi import APIRouter

from skill_manager.models.skill import SkillType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skill-types")


@router.get(
    "",
    response_model=List[str],
)
async def get_skill_types():
    """Returns a list of supported skill-types."""
    skill_types = [skill_type.value for skill_type in SkillType]

    logger.debug("get_skill_types {skill_types}".format(skill_types=skill_types))
    return skill_types
