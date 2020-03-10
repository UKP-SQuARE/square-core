# square-core
Frontend and QA backend server code

## Run locally (development)
The README.md in square-backend, square-frontend and reference-skill-example describes how to start the server locally for development.

## Docker-Compose
Run `docker-compose up [--build]` to run front- and backend along with a Postgres DB in production mode.
This starts no additional skill server.

[docker-compose-skill.yaml](docker-compose-skill.yaml) gives an example on how to add skill server to the cluster.
However, skill server can also be run independently from the core server.  
If a skill server is run in the same cluster, then its container name should be used as host and not 127.0.0.1.
The client will say it is not available, but the backend server can resolve it. 