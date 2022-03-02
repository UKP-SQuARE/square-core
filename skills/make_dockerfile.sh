#!/bin/bash
SKILL=$1
PORT=$2

sed -e "s/%%SKILL%%/$SKILL/g" -e "s/%%PORT%%/$PORT/g" Dockerfile.template > "$SKILL.Dockerfile"
