#!/bin/bash
set -euo pipefail

export IMAGE_TAG="${1:?Usage: deploy-prod.sh <image-tag>}"

cd /opt/foxtail/prod
docker compose pull app worker
docker compose run --rm app django-admin migrate --noinput

if docker rollout --version &>/dev/null 2>&1; then
    docker rollout app
    docker compose up -d --remove-orphans worker
else
    docker compose up -d --remove-orphans
fi

docker image prune -f --filter "label=org.opencontainers.image.source=https://github.com/dmptrluke/foxtail"
