import os
import zipfile

import requests
from filelock import FileLock

from .config import settings
from .db import db


async def zip_application_package(path):
    zip_path = "./application.zip"
    lock_file = zip_path + ".lock"
    with FileLock(lock_file):
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with zipfile.ZipFile(zip_path, "a") as zip_archive:
            for root, dirs, files in os.walk(path):

                for file in files:
                    zip_archive.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
        return zip_path


async def upload_new_schema(path):
    url = settings.VESPA_CONFIG_URL + "/application/v2/tenant/default/prepareandactivate"

    zip_path = await zip_application_package(path)

    header = {
        "Content-Type": "application/zip",
    }
    with open(zip_path, "rb") as file:
        data = file.read()
    response = requests.post(url, data=data, headers=header)

    if response.status_code != 200:
        raise RuntimeError(
            "Status code " + str(response.status_code) + " doing POST at " + url + ":\n" + response.text
        )
        return False

    else:
        print("Successful upload")  # parsed

        return True


async def generate_and_upload_package(allow_content_removal: bool = False):
    await db.export(settings.VESPA_APP_EXPORT_PATH, allow_content_removal=allow_content_removal)
    return await upload_new_schema(settings.VESPA_APP_EXPORT_PATH)
