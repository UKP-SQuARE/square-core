from datetime import datetime
import logging
from bson import ObjectId
from itertools import chain
from typing import List, Optional

import pymongo
import requests
from fastapi import FastAPI
from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from skill_manager.models import Skill, SkillType, Prediction
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
async def update_skill(id: str, data: dict):
    skill = await get_skill_by_id(id)

    for k, v in data.items():
        if hasattr(skill, k):
            setattr(skill, k, v)

    _ = app.state.skill_manager_db.skills.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": data}
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
    skill = await update_skill(id, skill.dict())

    logger.debug("publish_skill: {skill}".format(skill=skill))
    return skill


@app.post("/skill/{id}/unpublish", response_model=Skill, status_code=201)
async def unpublish_skill(id: str):
    skill = await get_skill_by_id(id)
    skill.published = False
    skill = await update_skill(id, skill.dict())

    logger.debug("unpublish_skill: {skill}".format(skill=skill))
    return skill


@app.post("/skill/{id}/query", response_model=QueryOutput)
async def query_skill(query_request: QueryRequest, id: str):
    logger.info(
        "received query: {query} for skill {id}".format(
            query=query_request.json(), id=id
        )
    )

    query = query_request.query
    user_id = query_request.user_id

    skill: Skill = await get_skill_by_id(id)

    default_skill_args = skill.default_skill_args
    if default_skill_args is not None:
        # add default skill args, potentially overwrite with query.skill_args
        query_request.skill_args = {**default_skill_args, **query_request.skill_args}

    # FIXME: Once UI sends context and answers seperatly, this code block can be deleted
    if (
        skill.skill_settings.requires_multiple_choices > 0
        and "answers" not in query_request.skill_args
    ):
        answers = query_request.skill_args["context"].split("\n")
        if skill.skill_settings.requires_context:
            query_request.skill_args["context"], *answers = answers
        query_request.skill_args["answers"] = answers

    response = requests.post(f"{skill.url}/query", json=query_request.dict())
    if response.status_code > 201:
        logger.exception(response.content)
        response.raise_for_status()
    predictions = response.json()
    logger.debug(
        "predictions from skill: {predictions}".format(predictions=predictions)
    )

    # save prediction to mongodb
    mongo_prediction = Prediction(
        skill_id=skill.id,
        skill_name=skill.name,
        query=query,
        user_id=user_id,
        predictions=predictions["predictions"],
    )
    _ = app.state.skill_manager_db.predictions.insert_one(
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
