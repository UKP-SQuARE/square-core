from .bing import BingSearch
from ..routers.dependencies import get_storage_connector, get_mongo_client
from .es.connector import ElasticsearchConnector
from .mongo import MongoClient
from ..models.datastore import DatastoreRequest, DatastoreField
from .config import settings
import requests
import time
from fastapi import Request
import jwt

import logging


def wait_for_up(url: str, ntries=100) -> None:
    for _ in range(ntries):
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Connected to {url}")
            return
        time.sleep(1)
    raise RuntimeError(f"Could not connect to {url}")


logger = logging.getLogger(__name__)

async def startup_event_handler():
    # wait until the elasticsearch docker container is ready
    wait_for_up(settings.ES_URL)

    # datastore_name is bing_search
    datastore_name = BingSearch.datastore_name
    # create placehoder DatastoreRequest
    fields = DatastoreRequest(
        __root__=[DatastoreField(name="title", type="text"),
                  DatastoreField(name="text", type="text")]
    )
    binding_item_type = 'datastore'
    conn: ElasticsearchConnector = get_storage_connector()
    mongo: MongoClient = get_mongo_client()
    try:
        # check if datastore exists
        schema = await conn.get_datastore(datastore_name)

        success = False
        if schema is None:
            # create datastore if it doesn't exist
            schema = fields.to_datastore(datastore_name)
            success = await conn.add_datastore(schema)
            if success:
                
                # create a token with the default user_id
                token = jwt.encode({"preferred_username": "LOCAL_SQUARE_USER"}, "secret", algorithm="HS256")
                # create a mock scope
                socpe =  {
                    'type': 'http',
                    'headers': [(b'authorization', b'Bearer ' + token.encode('utf-8'))], 
                }
                # create a mock request
                request = Request(scope=socpe)

                await mongo.new_binding(request, datastore_name, binding_item_type)
                logger.info(f"Created datastore {datastore_name}")
            else:
                logger.error(f"Failed to create datastore {datastore_name}")
            await conn.commit_changes()
        else:
            logger.info(f"Datastore {datastore_name} already exists")
    except Exception as e:
        logger.error(
            f"Failed to create datastore {datastore_name}: {e}")
