#!/bin/bash
# Distributes tar ball of ElkJsonFormatter to parent directories listed in $services
# Please update version when creating new ElkJsonFormatter 
version=${1:-"0.0.2"}
services=(square-backend datastore-api square-model-inference-api/auth_server square-model-inference-api/inference_server skills/qa-retrieve-span-skill skills/qa-boolq-skill skills/qa-commonsense-qa-skill skills/qa-squad-v2-skill)
for service in ${services[@]}; do
    cp dist/ElkJsonFormatter-${version}.tar.gz ../$service/ElkJsonFormatter.tar.gz
done
