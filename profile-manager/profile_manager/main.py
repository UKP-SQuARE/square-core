import logging
import os
import yaml
from pymongo.errors import BulkWriteError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from profile_manager import mongo_client, redis_client
from profile_manager.routers.api import router

logger = logging.getLogger(__name__)

app = FastAPI(title="Profile-Manager API", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router, prefix="/api")


def add_prefix_to_openapi():
    global app
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Profile-Manager API",
        version="0.0.1",
        description="API reference for profile-manager.",
        routes=app.routes,
    )
    prefix = os.getenv("API_PREFIX", "profile-manager")

    if prefix == "":
        return openapi_schema

    replaced_keys = {}
    for api_route in openapi_schema["paths"].keys():
        api_route_prefix = api_route.split("/")
        api_route_prefix.insert(2, prefix)
        api_route_prefix = "/".join(api_route_prefix)

        logging.debug(f"replacing: {api_route} with {api_route_prefix}")
        replaced_keys[api_route] = api_route_prefix

    openapi_schema["paths"] = {
        replaced_keys[k]: v for k, v in openapi_schema["paths"].items()
    }
    return openapi_schema


app.openapi_schema = add_prefix_to_openapi()


@app.on_event("startup")
async def on_startup():
    mongo_client.connect()
    redis_client.connect()
    await load_llms_to_db()

async def load_llms_to_db():
    llm_file_path = '/db/llm.yaml'  # Replace with your YAML file path
    with open(llm_file_path, 'r') as file:
        llm_data = yaml.safe_load(file)

    llms = llm_data.get('llms', [])

    if llms:
        db = mongo_client.client.daspChatBotRating
        try:
            db.create_collection('LLM')
            logger.info("LLM collection created in daspChatBotRating database.")
        except Exception as e:
            logger.info("LLM collection already exists in daspChatBotRating database.")
        for llm in llms:
            # Check if an LLM with the same Name already exists
            if not db.LLM.find_one({"Name": llm["Name"]}):
                try:
                    result = db.LLM.insert_one(llm)
                    logger.info(f"Inserted LLM '{llm['Name']}' into the database.")
                except Exception as e:
                    logger.error(f"Error inserting LLM '{llm['Name']}' into the database: {e}")
            else:
                logger.info(f"LLM '{llm['Name']}' already exists in the database.")



@app.on_event("shutdown")
def on_shutdown():
    mongo_client.close()
    redis_client.close()