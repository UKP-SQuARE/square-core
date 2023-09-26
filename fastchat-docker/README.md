# FastChat-docker
Sophisticated docker builds for parent project [lm-sys/FastChat](https://github.com/lm-sys/FastChat). 

![example workflow](https://github.com/localagi/FastChat-docker/actions/workflows/publish-docker.yml/badge.svg?branch=main)

Easy setup. Compatible. Tweakable. Scaleable.

#### Supported platforms
`amd64`, `arm64`

#### Supported versions
Containers follow the version scheme of the parent project

`main` (default), `v0.2.9`, etc.

See [Releases](../../releases)

## Prerequisites

* `docker` and `docker compose` are available on your system

##### NVIDIA card required
These containers require `nvidia-container-toolkit` installed and reboot

## Run

Short description what it does
The following wil get all im

* get `docker-compose.yml` (clone repo, copy or else) 
* Run `docker compose up`
* wait for model download (~7GB)
* open/refresh `http://localhost:3000` 

### Runtime options
[] TODO Environment variables to set for the specific service

#### version selection `FASTCHAT_VERSION`
Prepend, e.g. `FASTCHAT_VERSION=v0.2.9`

### Get the latest builds / update
`docker compose pull`

### Cleanup
`docker compose rm`

## Contributing

When there is a new version and there is need of builds or you require the latest main build, feel free to open an issue

## Problems?

Open an issue on the [Issue Tracker](../../issues)

## Limitations
We cannot support issues regarding the base software. Please refer to the main project page mentioned in the second line of this card.

