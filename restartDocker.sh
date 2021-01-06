#!/bin/bash


#stop container 
docker-compose down

# remove everything
docker system prune -a --volumes

# restart
docker-compose -f docker-compose.yaml up

