import logging
import os
import yaml
from pymongo.errors import BulkWriteError, CollectionInvalid
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
    await load_certificates_to_db()
    await load_badges_to_db()

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

async def load_certificates_to_db():
    certificate_file_path = '/db/certificate.yaml'  # Replace with your YAML file path
    with open(certificate_file_path, 'r') as file:
        certificate_data = yaml.safe_load(file)

    certificates = certificate_data.get('certificates', [])

    if certificates:
        db = mongo_client.client.daspChatBotRating

        # Attempt to create the 'Certificates' collection
        try:
            db.create_collection('Certificates')
            logger.info("Certificates collection created in daspChatBotRating database.")
        except CollectionInvalid:
            logger.info("Certificates collection already exists in daspChatBotRating database.")

        for certificate in certificates:
            # Insert the certificate into the database
            if not db.Certificate.find_one({"title": certificate["title"]}):
                try:
                    result = db.Certificate.insert_one(certificate)
                    logger.info(f"Inserted certificate with ID '{certificate['_id']}' into the database.")
                except Exception as e:
                    logger.error(f"Error inserting certificate with ID '{certificate['_id']}' into the database: {e}")
            else:
                logger.info(f"Certificate '{certificate['title']}' already exists in the database.")

async def load_badges_to_db():
    badge_file_path = '/db/badge.yaml'  # Replace with your YAML file path
    with open(badge_file_path, 'r') as file:
        badge_data = yaml.safe_load(file)

    badges = badge_data.get('badges', [])  # Assuming the top-level element is a list of badges

    if badges:
        db = mongo_client.client.daspChatBotRating

        # Attempt to create the 'Badges' collection
        try:
            db.create_collection('Badges')
            logger.info("Badges collection created in daspChatBotRating database.")
        except CollectionInvalid:
            logger.info("Badges collection already exists in daspChatBotRating database.")

        for badge in badges:
            # Insert the badge into the database
            if not db.Badge.find_one({"title": badge["title"]}):  # Check if the badge already exists
                try:
                    result = db.Badge.insert_one(badge)
                    logger.info(f"Inserted badge '{badge['title']}' into the database.")
                except Exception as e:
                    logger.error(f"Error inserting badge '{badge['title']}' into the database: {e}")
            else:
                logger.info(f"Badge '{badge['title']}' already exists in the database.")

@app.on_event("shutdown")
def on_shutdown():
    mongo_client.close()
    redis_client.close()