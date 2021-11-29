import logging
from bson import ObjectId
from itertools import chain
from typing import List, Optional

import pymongo
import requests
from fastapi import FastAPI, Request

from skill_manager.models import Skill, SkillType
from skill_manager.mongo_settings import MongoSettings

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    mongo_settings = MongoSettings()
    app.state.mongo_client = pymongo.MongoClient(mongo_settings.connection_url)
    app.state.skill_manager_db = app.state.mongo_client.skill_manager


@app.get("/skill-types", response_model=List[str])
async def get_skill_types():
    skill_types = [skill_type.value for skill_type in SkillType]

    logger.debug("get_skill_types {skill_types}".format(skill_types=skill_types))
    return skill_types


@app.get("/skill/{id}", response_model=Skill)
async def get_skill_by_id(id: Optional[str] = None):
    skill = Skill.from_mongo(
        app.state.skill_manager_db.skills.find_one({"_id": ObjectId(id)})
    )

    logger.debug("get_skill_by_id: {skill}".format(skill=skill))
    return skill


@app.get("/skill", response_model=List[Skill])
async def get_skills(user_id: Optional[str] = None):
    if user_id:
        user_skills = app.state.skill_manager_db.skills.find({"user_id": user_id})
    else:
        user_skills = []
    published_skills = app.state.skill_manager_db.skills.find({"published": True})
    skills = [Skill.from_mongo(s) for s in chain(user_skills, published_skills)]

    logger.debug("get_skills: {skills}".format(skills=skills))
    return skills


@app.post("/skill", response_model=Skill, status_code=201)
async def create_skill(skill: Skill):

    skill_id = app.state.skill_manager_db.skills.insert_one(skill.mongo()).inserted_id
    skill = await get_skill_by_id(skill_id)

    logger.debug("create_skill: {skill}".format(skill=skill))
    return skill


@app.put("/skill/{id}", response_model=Skill)
async def update_skill(id: str, request: Request):
    request = await request.json()
    skill = await get_skill_by_id(id)

    for k, v in request.items():
        if hasattr(skill, k):
            setattr(skill, k, v)
    
    _ = app.state.skill_manager_db.skills.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": skill.mongo()}
    )
    updated_skill = await get_skill_by_id(id)

    logger.debug(
        "update_skill: old: {skill} updated: {updated_skill}".format(
            skill=skill, updated_skill=updated_skill
        )
    )
    return skill


@app.delete("/skill/{id}", status_code=204)
async def delete_skill(id: str):
    delete_result = app.state.skill_manager_db.skills.delete_one({"_id": ObjectId(id)})
    logger.debug("delete_skill: {id}".format(id=id))
    if delete_result.acknowledged:
        return
    else:
        raise RuntimeError(delete_result.raw_result)


@app.post("/skill/{id}/publish", response_model=Skill, status_code=201)
async def publish_skill(id: str):
    skill = await get_skill_by_id(id)
    skill.published = True
    skill = await update_skill(id, skill)

    logger.debug("publish_skill: {skill}".format(skill=skill))
    return skill


@app.post("/skill/{id}/unpublish", response_model=Skill, status_code=201)
async def unpublish_skill(id: str):
    skill = await get_skill_by_id(id)
    skill.published = False
    skill = await update_skill(id, skill)

    logger.debug("unpublish_skill: {skill}".format(skill=skill))
    return skill


@app.post("/skill/{id}/query")
async def query_skill(request: Request, id: str):
    request = await request.json()
    skill = await get_skill_by_id(id)
    response = requests.post(f"{skill.url}/query", json=request)
    response.raise_for_status()

    prediction = response.json()
    logger.debug(
        "query_skill: request: {request} prediction: {prediction}".format(
            request=request, prediction=prediction
        )
    )
    return prediction
