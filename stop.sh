#!/bin/sh

set -e

docker compose down --remove-orphans

if [ "$1" = "--prune" ]; then
  docker system prune -af; docker volume prune -af; docker network prune -f;
fi
