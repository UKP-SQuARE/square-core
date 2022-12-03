from .bing import BingSearch
from ..routers.dependencies import get_storage_connector, get_mongo_client
from .es.connector import ElasticsearchConnector
from .mongo import MongoClient
from ..models.datastore import DatastoreRequest, DatastoreField
from .config import settings
import requests
import time

import logging


def wait_for_up(url: str, ntries=100) -> None:
    for _ in range(ntries):
        try:
            # import ipdb; ipdb.set_trace()
            response = requests.get(url)
            if response.status_code == 200:
                logger.info(f"Connected to {url}")
                break
        except:
            time.sleep(1)

logger = logging.getLogger(__name__)

async def startup_event_handler():
    # wait until the elasticsearch docker container is ready
    # TODO: make sure this works also during testing
    wait_for_up(settings.ES_URL)

    # datastore_name is bing_search
    datastore_name = BingSearch.datastore_name
    # create placehoder DatastoreRequest
    fields = DatastoreRequest(
        __root__=[DatastoreField(name="title", type="text"),
                  DatastoreField(name="text", type="text")]
    )
    binding_item_type = 'datastore'
    # default user_id
    user_id = 'LOCAL_SQUARE_USER'
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
                # None is in place of request since it is not available at this point
                await mongo.new_binding(None, datastore_name, binding_item_type, user_id)
                logger.info(f"Created datastore {datastore_name}")
            else:
                logger.error(f"Failed to create datastore {datastore_name}")
            await conn.commit_changes()
        else:
            logger.info(f"Datastore {datastore_name} already exists")
    except Exception as e:
        logger.error(
            f"Failed to create datastore {datastore_name}: {e}")
