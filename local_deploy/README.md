For local deployment of the minimal version, please run under the root folder:
```bash
bash install-local.sh
```
During the process, a `private_key.pem` file will be generated to the `local_deploy` folder. This file will be used for authentification (note that this part is different from the full master version).

Then, run the example script to upload a Datastore and do search:
```bash
export SQUARE_PRIVATE_KEY_FILE=${PWD}/local_deploy/private_key.pem; python local_deploy/upload_ds.py
```