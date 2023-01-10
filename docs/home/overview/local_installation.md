---
sidebar_position: 6
---
# Local Installation

## Requirements
To run UKP-SQuARE locally, you need the following software:
* [docker](https://docs.docker.com/get-docker/)
* [docker-compose](https://docs.docker.com/compose/install/#install-compose)
* [ytt](https://carvel.dev/ytt/)
* [jq](https://stedolan.github.io/jq/download/)

## Install
Next change the `environment` to `local` and `os` to your operating system in the [config.yaml](https://github.com/UKP-SQuARE/square-core/tree/master/config.yaml).  
Next change the `environment` to `local` and `os` to your operating system in the [config.yaml](https://github.com/UKP-SQuARE/square-core/tree/master/config.yaml).  
Now, modify your `/etc/hosts` to contain:
```
127.0.0.1   square.ukp-lab.localhost
```  
For installation we provide a script that takes care of the entire setup for you. After installing the previous [requirements](#requirements), simply run:
```bash
bash install.sh
```
## Run 
Finally, you can run the full system with docker-compose. Before doing so, you might want to reduce the number of models running depending on your resources. To do so, remove the respective services from the docker-compose.
```bash
docker-compose up -d
```
Check with `docker-compose logs -f` if all systems have started successfully. Once they are up and running go to [square.ukp-lab.localhost](https://square.ukp-lab.localhost).
👉 Accept that the browser cannot verify the certificate.