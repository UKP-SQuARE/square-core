#!/bin/bash
# Distributes tar ball of ElkJsonFormatter to parent directories listed in $services
# Please update version when creating new ElkJsonFormatter 
version=${1:-"0.0.2"}
services=(square-backend)
for service in $services; do
    cp dist/ElkJsonFormatter-${version}.tar.gz ../$service/ElkJsonFormatter.tar.gz
done
