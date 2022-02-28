#!/bin/bash

for SKILL_PORT in $(jq -c -r '.[] | [.name, .port]' skills.json) ; do
    SKILL_PORT=($(echo $SKILL_PORT | tr -d '[],' | sed 's/\"\"/\" \"/g' | tr -d \"))
    SKILL=${SKILL_PORT[0]}
    PORT=${SKILL_PORT[1]}

    sed -e "s/%%SKILL%%/$SKILL/g" -e "s/%%PORT%%/$PORT/g" Dockerfile.template > "$SKILL.Dockerfile"
done
