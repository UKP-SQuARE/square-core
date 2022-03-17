import json
import logging
import os
from http.client import HTTPException
from typing import List, Optional

import jwt
import requests
from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from skill_manager import mongo_client
from skill_manager.keycloak_api import KeycloakAPI
from skill_manager.models import Prediction, Skill, SkillType
from square_auth.auth import Auth
from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from skill_manager.routers import client_credentials

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/skill")


async def get_payload_from_token(request: Request):
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)
    return {"realm": realm, "username": payload["preferred_username"]}


def has_auth_header(request: Request):
    return request.headers.get("Authorization", "").lower().startswith("bearer")


@router.get(
    "/{id}",
    response_model=Skill,
)
async def get_skill_by_id(request: Request, id: str = None):
    """Returns the saved skill information."""
    skill = Skill.from_mongo(
        mongo_client.client.skill_manager.skills.find_one({"_id": ObjectId(id)})
    )
    logger.debug("get_skill_by_id: {skill}".format(skill=skill))

    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]
        if not skill.published and not skill.user_id == user_id:
            raise HTTPException(403)

    return skill


@router.get(
    "",
    response_model=List[Skill],
)
async def get_skills(request: Request, user_id: Optional[str] = None):
    """Returns all skills that a user has access to. A user has access to
    all public skills, and private skill created by them."""
    mongo_query = {"published": True}
    if user_id or has_auth_header(request):
        if has_auth_header(request):
            payload = await get_payload_from_token(request)
            user_id = ["username"]
        mongo_query = {"$or": [mongo_query, {"user_id": user_id}]}

    skills = mongo_client.client.skill_manager.skills.find(mongo_query)
    skills = [Skill.from_mongo(s) for s in skills]

    logger.debug("get_skills: {skills}".format(skills=skills))
    return skills


@router.post(
    "",
    response_model=Skill,
    status_code=201,
)
async def create_skill(
    skill: Skill, request: Request, keycloak_api=Depends(KeycloakAPI)
):
    """Creates a new skill and saves it."""

    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        realm = payload["realm"]
        username = payload["username"]
    else:
        realm = "square"
        username = skill.user_id

    client = keycloak_api.create_client(
        realm=realm, username=username, skill_name=skill.name
    )
    skill.client_id = client["clientId"]
    skill_id = mongo_client.client.skill_manager.skills.insert_one(
        skill.mongo()
    ).inserted_id
    skill = await get_skill_by_id(request, skill_id)
    logger.debug("create_skill: {skill}".format(skill=skill))

    # set the secret *after* saving the skill to mongoDB, so the secret will be
    # returned, but not logged and not persisted.
    skill.client_secret = client["secret"]
    return skill


@router.put(
    "/{id}",
    response_model=Skill,
)
async def update_skill(request: Request, id: str, data: dict):
    """Updates a skill with the provided data."""
    skill = await get_skill_by_id(request, id)

    for k, v in data.items():
        if hasattr(skill, k):
            setattr(skill, k, v)

    _ = mongo_client.client.skill_manager.skills.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": data}
    )
    updated_skill = await get_skill_by_id(request, id)

    logger.debug(
        "update_skill: old: {skill} updated: {updated_skill}".format(
            skill=skill, updated_skill=updated_skill
        )
    )
    return skill


@router.delete("/{id}", status_code=204)
async def delete_skill(request: Request, id: str):
    """Deletes a skill."""
    _ = await get_skill_by_id(request, id)

    delete_result = mongo_client.client.skill_manager.skills.delete_one(
        {"_id": ObjectId(id)}
    )
    logger.debug("delete_skill: {id}".format(id=id))
    if delete_result.acknowledged:
        return
    else:
        raise RuntimeError(delete_result.raw_result)


@router.post(
    "/{id}/publish",
    response_model=Skill,
    status_code=201,
)
async def publish_skill(request: Request, id: str):
    """Makes a skill publicly available."""
    skill = await get_skill_by_id(request, id)
    skill.published = True
    skill = await update_skill(request, id, skill.dict())

    logger.debug("publish_skill: {skill}".format(skill=skill))
    return skill


@router.post(
    "/{id}/unpublish",
    response_model=Skill,
    status_code=201,
)
async def unpublish_skill(request: Request, id: str):
    """Makes a skill private."""
    skill = await get_skill_by_id(request, id)
    skill.published = False
    skill = await update_skill(request, id, skill.dict())

    logger.debug("unpublish_skill: {skill}".format(skill=skill))
    return skill


@router.post(
    "/{id}/query",
    response_model=QueryOutput,
)
async def query_skill(
    request: Request,
    query_request: QueryRequest,
    id: str,
    token: str = Depends(client_credentials),
):
    """Sends a query to the respective skill and returns its prediction."""
    logger.info(
        "received query: {query} for skill {id}".format(
            query=query_request.json(), id=id
        )
    )

    query = query_request.query
    user_id = query_request.user_id

    skill: Skill = await get_skill_by_id(request, id)
    query_request.skill = json.loads(skill.json())

    default_skill_args = skill.default_skill_args
    if default_skill_args is not None:
        # add default skill args, potentially overwrite with query.skill_args
        query_request.skill_args = {**default_skill_args, **query_request.skill_args}

    # FIXME: Once UI sends context and answers seperatly, this code block can be deleted
    if (
        skill.skill_type == SkillType.multiple_choice
        and "choices" not in query_request.skill_args
    ):
        choices = query_request.skill_args["context"].split("\n")
        if skill.skill_settings.requires_context:
            query_request.skill_args["context"], *choices = choices
        query_request.skill_args["choices"] = choices

    response = requests.post(
        f"{skill.url}/query",
        headers={"Authorization": f"Bearer {token}"},
        json=query_request.dict(),
    )
    if response.status_code > 201:
        logger.exception(response.content)
        response.raise_for_status()
    predictions = QueryOutput.parse_obj(response.json())
    logger.debug(
        "predictions from skill: {predictions}".format(predictions=predictions)
    )

    # save prediction to mongodb
    mongo_prediction = Prediction(
        skill_id=skill.id,
        skill_name=skill.name,
        query=query,
        user_id=user_id,
        predictions=predictions.predictions,
    )
    _ = mongo_client.client.skill_manager.predictions.insert_one(
        mongo_prediction.mongo()
    ).inserted_id
    logger.debug(
        "prediction saved {mongo_prediction}".format(
            mongo_prediction=mongo_prediction.json(),
        )
    )

    logger.debug(
        "query_skill: query_request: {query_request} predictions: {predictions}".format(
            query_request=query_request.json(), predictions=predictions
        )
    )
    return predictions
