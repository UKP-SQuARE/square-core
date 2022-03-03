#!/bin/bash
SKILL=$1

sed -e "s/%%SKILL%%/$SKILL/g" Dockerfile.template > "$SKILL.Dockerfile"
