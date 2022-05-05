import logging
from typing import Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, Request, Path
from square_auth.auth import Auth
from skill_manager import mongo_client
from skill_manager.core.keycloak_client import KeycloakClient

from skill_manager.models.skill_template import SkillTemplate


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skill-templates")

auth = Auth()


@router.get("", response_model=List[SkillTemplate])
async def get_skill_templates():

    skill_templates = mongo_client.client.skill_manager.skill_templates.find({})
    skill_templates = [SkillTemplate.from_mongo(s) for s in skill_templates]

    return skill_templates


@router.get("/{id}", response_model=SkillTemplate)
async def get_skill_template_by_id(skill_template_id=Path(..., alias="id")):
    skill_template = mongo_client.client.skill_manager.skill_templates.find_one(
        {"_id": ObjectId(skill_template_id)}
    )
    skill_template = SkillTemplate.from_mongo(skill_template)
    return skill_template


@router.post("", response_model=SkillTemplate, status_code=201)
async def create_skill_template(
    skill_template: SkillTemplate,
    keycloak_client: KeycloakClient = Depends(KeycloakClient),
    token_payload: Dict = Depends(auth),
):
    # create a new client in keycloak
    realm = token_payload["realm"]
    username = token_payload["username"]
    client = keycloak_client.create_client(
        realm=realm, username=username, skill_name=skill_template.name
    )
    skill_template.client_id = client["clientId"]
    
    # save skill template in mongo db
    skill_template_id = mongo_client.client.skill_manager.skill_templates.insert_one(
        skill_template.mongo()
    ).inserted_id
    skill_template.user_id = username
    skill_template.id = skill_template_id

    return skill_template


@router.put("/{id}", response_model=SkillTemplate)
async def update_skill_template(data: dict, skill_template_id=Path(..., alias="id")):
    skill_template = await get_skill_template_by_id(skill_template_id)
    for k, v in data.items():
        if hasattr(skill_template, k):
            setattr(skill_template, k, v)

    _ = mongo_client.client.skill_manager.skill_templates.find_one_and_update(
        {"_id": ObjectId(skill_template_id)}, {"$set": skill_template.dict()}
    )
    updated_skill_template = await get_skill_template_by_id(skill_template_id)

    return updated_skill_template


@router.delete("/{id}", status_code=204)
async def delete_skill_template(skill_template_id=Path(..., alias="id")):

    delete_result = mongo_client.client.skill_manager.skill_templates.delete_one(
        {"_id": ObjectId(skill_template_id)}
    )
    logger.debug("delete skill template with  id={id}".format(id=skill_template_id))
    if delete_result.acknowledged:
        return
    else:
        raise RuntimeError(delete_result.raw_result)
