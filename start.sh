#!/bin/bash

set -e

# ##################################################
# Shared                                           #
# ##################################################

# Global Variables

SRV_DIR="/srv/sdrhub"
ENV_FILE="${SRV_DIR}/.env"

# Environment Variables

if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
else
  echo "Error: Environment file not found at $ENV_FILE" >&2
  exit 1
fi

# ##################################################
# Docker                                           #
# ##################################################

if [ "$1" = "--restart" ]; then
  docker compose down --remove-orphans
fi

docker compose up -d --force-recreate

# ##################################################
# Configure Ntfy                                   #
# ##################################################

echo "Waiting for the sdrhub-ntfy container to start..."

for i in $(seq 1 60); do
  if docker inspect -f '{{.State.Running}}' sdrhub-ntfy 2>/dev/null | grep -q true; then
    break
  else
    sleep 1
  fi
done

echo "Creating Ntfy user if it does not already exist..."

if printf "%s\n%s\n" "$NTFY_PASSWORD" "$NTFY_PASSWORD" | docker exec -i sdrhub-ntfy ntfy user add --role=admin "$NTFY_USER" 2>/dev/null; then
  echo "User $NTFY_USER created."
fi
