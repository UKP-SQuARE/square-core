import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from skill_manager import mongo_client
from skill_manager.routers.api import router

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)


@app.on_event("startup")
def on_startup():
    mongo_client.connect()

@app.on_event("shutdown")
def on_startup():
    mongo_client.close()

# @app.on_event("startup")
# def on_startup():
#     mongo_settings = MongoSettings()
#     app.state.mongo_client = pymongo.MongoClient(mongo_settings.connection_url)
#     app.state.skill_manager_db = app.state.mongo_client.skill_manager

# @app.get(
#     "/api/health/heartbeat",
#     response_model=HeartbeatResult,
# )
# async def heartbeat():
#     """Checks if the skill-manager instance is still up and running."""
#     return HeartbeatResult(is_alive=True)


# @app.get(
#     "/api/health/skill-heartbeat",
#     response_model=HeartbeatResult,
# )
# async def skill_heartbeat(skill_url: str):
#     """Checks if a skill is still up and running."""
#     skill_health_url = urljoin(skill_url, "health/heartbeat")

#     skill_heartbeat_response = requests.get(skill_health_url)
#     logger.debug(
#         "skill at {} health {}".format(
#             skill_health_url, skill_heartbeat_response.json()
#         )
#     )

#     return skill_heartbeat_response.json()


# @app.get(
#     "/api/skill-types",
#     response_model=List[str],
# )
# async def get_skill_types():
#     """Returns a list of supported skill-types."""
#     skill_types = [skill_type.value for skill_type in SkillType]

#     logger.debug("get_skill_types {skill_types}".format(skill_types=skill_types))
#     return skill_types


# @app.get(
#     "/api/skill/{id}",
#     response_model=Skill,
# )
# async def get_skill_by_id(id: Optional[str] = None):
#     """Returns the saved skill information."""
#     skill = Skill.from_mongo(
#         app.state.skill_manager_db.skills.find_one({"_id": ObjectId(id)})
#     )

#     logger.debug("get_skill_by_id: {skill}".format(skill=skill))
#     return skill


# @app.get(
#     "/api/skill",
#     response_model=List[Skill],
# )
# async def get_skills(user_id: Optional[str] = None):
#     """Returns all skills that a user has access to. A user has access to 
#     all public skills, and private skill created by them."""
#     mongo_query = {"published": True}
#     if user_id:
#         mongo_query = {"$or": [mongo_query, {"user_id": user_id}]}

#     skills = app.state.skill_manager_db.skills.find(mongo_query)
#     skills = [Skill.from_mongo(s) for s in skills]

#     logger.debug("get_skills: {skills}".format(skills=skills))
#     return skills


# @app.post(
#     "/api/skill",
#     response_model=Skill,
#     status_code=201,
# )
# async def create_skill(skill: Skill):
#     """Creates a new skill and saves it."""
#     skill_id = app.state.skill_manager_db.skills.insert_one(skill.mongo()).inserted_id
#     skill = await get_skill_by_id(skill_id)

#     logger.debug("create_skill: {skill}".format(skill=skill))
#     return skill


# @app.put(
#     "/api/skill/{id}",
#     response_model=Skill,
# )
# async def update_skill(id: str, data: dict):
#     """Updates a skill with the provided data."""
#     skill = await get_skill_by_id(id)

#     for k, v in data.items():
#         if hasattr(skill, k):
#             setattr(skill, k, v)

#     _ = app.state.skill_manager_db.skills.find_one_and_update(
#         {"_id": ObjectId(id)}, {"$set": data}
#     )
#     updated_skill = await get_skill_by_id(id)

#     logger.debug(
#         "update_skill: old: {skill} updated: {updated_skill}".format(
#             skill=skill, updated_skill=updated_skill
#         )
#     )
#     return skill


# @app.delete("/api/skill/{id}", status_code=204)
# async def delete_skill(id: str):
#     """Deletes a skill."""
#     delete_result = app.state.skill_manager_db.skills.delete_one({"_id": ObjectId(id)})
#     logger.debug("delete_skill: {id}".format(id=id))
#     if delete_result.acknowledged:
#         return
#     else:
#         raise RuntimeError(delete_result.raw_result)


# @app.post(
#     "/api/skill/{id}/publish",
#     response_model=Skill,
#     status_code=201,
# )
# async def publish_skill(id: str):
#     """Makes a skill publicly available."""
#     skill = await get_skill_by_id(id)
#     skill.published = True
#     skill = await update_skill(id, skill.dict())

#     logger.debug("publish_skill: {skill}".format(skill=skill))
#     return skill


# @app.post(
#     "/api/skill/{id}/unpublish",
#     response_model=Skill,
#     status_code=201,
# )
# async def unpublish_skill(id: str):
#     """Makes a skill private."""
#     skill = await get_skill_by_id(id)
#     skill.published = False
#     skill = await update_skill(id, skill.dict())

#     logger.debug("unpublish_skill: {skill}".format(skill=skill))
#     return skill


# @app.post(
#     "/api/skill/{id}/query",
#     response_model=QueryOutput,
# )
# async def query_skill(query_request: QueryRequest, id: str):
#     """Sends a query to the respective skill and returns its prediction."""
#     logger.info(
#         "received query: {query} for skill {id}".format(
#             query=query_request.json(), id=id
#         )
#     )

#     query = query_request.query
#     user_id = query_request.user_id

#     skill: Skill = await get_skill_by_id(id)

#     default_skill_args = skill.default_skill_args
#     if default_skill_args is not None:
#         # add default skill args, potentially overwrite with query.skill_args
#         query_request.skill_args = {**default_skill_args, **query_request.skill_args}

#     # FIXME: Once UI sends context and answers seperatly, this code block can be deleted
#     if (
#         skill.skill_settings.requires_multiple_choices > 0
#         and "answers" not in query_request.skill_args
#     ):
#         answers = query_request.skill_args["context"].split("\n")
#         if skill.skill_settings.requires_context:
#             query_request.skill_args["context"], *answers = answers
#         query_request.skill_args["answers"] = answers

#     response = requests.post(f"{skill.url}/query", json=query_request.dict())
#     if response.status_code > 201:
#         logger.exception(response.content)
#         response.raise_for_status()
#     predictions = QueryOutput.parse_obj(response.json())
#     logger.debug(
#         "predictions from skill: {predictions}".format(predictions=predictions)
#     )

#     # save prediction to mongodb
#     mongo_prediction = Prediction(
#         skill_id=skill.id,
#         skill_name=skill.name,
#         query=query,
#         user_id=user_id,
#         predictions=predictions.predictions,
#     )
#     _ = app.state.skill_manager_db.predictions.insert_one(
#         mongo_prediction.mongo()
#     ).inserted_id
#     logger.debug(
#         "prediction saved {mongo_prediction}".format(
#             mongo_prediction=mongo_prediction.json(),
#         )
#     )

#     logger.debug(
#         "query_skill: query_request: {query_request} predictions: {predictions}".format(
#             query_request=query_request.json(), predictions=predictions
#         )
#     )
#     return predictions
