import ast
import asyncio
import base64
from io import BytesIO
import json
import os
import time
import aiohttp
import numpy as np
from utils import SharedVariables
import logging

logger = logging.getLogger(__name__)


def _decode_embeddings(encoded_string: str):
    encoded_string = encoded_string.encode()
    arr_binary = base64.decodebytes(encoded_string)
    arr = np.load(BytesIO(arr_binary))
    return arr


async def _wait_for_task(
    task_id: str,
    session: aiohttp.ClientSession,
    max_attempts=None,
    poll_interval=None,
):
    """
    Handling waiting for a task to finish. While the task has
    not finished request the result from the task_result
    endpoint and check whether it is finished
    Args:
            task_id (str): the id of the task
            max_attempts (int, optional): the maximum number of
            attempts to get the result. If this is None the
            self.max_attempts is used. The default is None.
            poll_interval (int, optional): the interval between the
            attempts to poll the results. If this is None
            self.poll_intervall is used. Defaults to None.
    """
    square_api_url = "https://traefik/api"
    verify_ssl = False

    if max_attempts is None:
        max_attempts = 50
    if poll_interval is None:
        poll_interval = 2
    attempts = 0
    result = None
    while attempts < max_attempts:
        attempts += 1
        async with session.get(
            url=f"{square_api_url}/main/task_result/{task_id}",
            headers={"Authorization": f"Bearer {SharedVariables.token}"},
            verify_ssl=verify_ssl,
        ) as response:
            resp = await response.text()

            if response.status == 200:
                result = ast.literal_eval(json.dumps(resp))
                break
            time.sleep(poll_interval)
    return json.loads(result)["result"]


async def encode_query():
    square_api_url = "https://traefik/api"
    model_identifier = "msmarco-distilbert-base-tas-b"
    prediction_method = "embedding"
    input_data = {
        "input": ["1 in 5 million in UK have abnormal PrP positivity."],
        "adapter_name": None,
        "task_kwargs": {"embedding_mode": "pooler"},
    }
    verify_ssl = False
    kwargs = {
        "url": f"{square_api_url}/main/{model_identifier}/{prediction_method}",
        "json": input_data,
        "headers": {"Authorization": f"Bearer {SharedVariables.token}"},
        "verify_ssl": verify_ssl,
    }

    print("=============", flush=True)
    my_conn = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=my_conn) as session:
        print("=============", flush=True)
        async with session.post(**kwargs) as response:
            print("=============", flush=True)
            result = await response.text()
            if response.status == 200:
                return await asyncio.ensure_future(
                    _wait_for_task(
                        ast.literal_eval(result)["task_id"],
                        session=session,
                    )
                )
            else:
                return response


if __name__ == "__main__":
    os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(os.getcwd(), "private_key.pem")
    response = asyncio.run(encode_query())
    print(response)
    print(_decode_embeddings(response["model_outputs"]["embeddings"]))
