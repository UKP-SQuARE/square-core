"""
An example script to call model API (to embed queries in this case). 
This script can be run both in the host machine or in a container from the SQuARE docker network.
If in container, please run `pip install square-model-client` before run this script (TODO: remove this requirement).
"""


import os
import asyncio
from utils import SharedVariables
from square_model_client import SQuAREModelClient


async def main():
    square_model_client = SQuAREModelClient()

    query = "When was TU Darmstadt established?"

    model_request = {
        "input": [query],
        "task_kwargs": {"embedding_mode": "cls"},
        "adapter_name": None,
    }

    model_api_output = await square_model_client(
        model_name="msmarco-distilbert-base-tas-b",
        pipeline="embedding",
        model_request=model_request,
    )
    print(*model_api_output["model_outputs"]["embeddings"], sep="\n")
    # [ 6.33941889e-02  1.83570012e-01  3.28775823e-01  9.42765027e-02
    # -2.52342403e-01  1.75254956e-01 -3.18139046e-01 -1.29823729e-01
    # 1.85419217e-01 -9.56809372e-02 ... -5.36588848e-01  1.10831536e-01]


if __name__ == "__main__":
    os.environ["SQUARE_API_URL"] = SharedVariables.model_url

    # Note, the SQuAREModelCLient is usually called within an endpoint that is async.
    # In that case, the following line is not needed.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
