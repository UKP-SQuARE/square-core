import json
import logging
from typing import List

from fastapi import APIRouter, Request
from square_auth.auth import Auth

from skill_manager import mongo_client
from skill_manager.auth_utils import get_payload_from_token, has_auth_header
from skill_manager.core.session_cache import SessionCache
from skill_manager.models import Skill

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dataset")

auth = Auth()

session_cache = SessionCache()


@router.get(
    "/{hf_name}/{dataset}",
    response_model=List[Skill],
)
@router.get(
    "/{dataset}",
    response_model=List[Skill],
)
async def get_skills_by_dataset(
    request: Request, hf_name: str = None, dataset: str = None
):
    """Returns all the skills that were trained on the given dataset."""
    if hf_name is not None:
        dataset = f"{hf_name}/dataset"

    user_avail_skills_query = {"published": True}
    if has_auth_header(request):
        payload = get_payload_from_token(request)
        user_id = payload["username"]
        user_avail_skills_query = {"$or": [{"published": True}, {"user_id": user_id}]}

    # make a mongo query that retrieves any skill that published is True or belongs to the user and dataset is in data_sets
    mongo_query = {"$and": [user_avail_skills_query, {"data_sets": dataset}]}

    logger.debug("Skill query: {query}".format(query=json.dumps(mongo_query)))
    skills = mongo_client.client.skill_manager.skills.find(mongo_query)
    skills = [Skill.from_mongo(s) for s in skills]

    logger.debug(
        "get_skills: {skills}".format(
            skills=", ".join(["{}:{}".format(s.name, str(s.id)) for s in skills])
        )
    )
    return skills
