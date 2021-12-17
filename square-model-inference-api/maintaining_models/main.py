import os

from fastapi import FastAPI
import docker
import re
import requests
from models import ModelRequest

API_URL = "http://host.docker.internal:80"
ABSOLUTE_PATH = "/run/desktop/mnt/host/c/Users/hster/PycharmProjects/square-core/square-model-inference-api"

app = FastAPI()
client = docker.APIClient(base_url='unix://var/run/docker.sock')


@app.get("/api/models")
async def get_all_models():
    lst_container = client.containers()
    lst_prefix = []
    for container in lst_container:
        if "model-inference-api" in client.inspect_container(container["Id"])["Name"] and "maintaining" not in \
                client.inspect_container(container["Id"])["Name"]:
            print(client.inspect_container(container["Id"]).keys())
            for identifier, label in client.inspect_container(container["Id"])["Config"]["Labels"].items():
                if "PathPrefix" in label:
                    print(label)
                    prefix = re.search('PathPrefix\(\`(.+?)\`\)', label).group(1)
                    lst_prefix.append(prefix)
    lst_models = []
    for prefix in lst_prefix:
        r = requests.get(url=API_URL + prefix + "/stats", auth=('admin', 'example_key'))
        if r.status_code == 200:
            lst_models.append(r.json())

    return lst_models

