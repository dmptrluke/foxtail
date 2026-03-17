#!/bin/bash
set -euo pipefail

export IMAGE_TAG="${1:?Usage: deploy-staging.sh <image-tag>}"

cd /opt/foxtail/staging
docker compose pull app worker
docker compose run --rm app django-admin migrate --noinput
docker compose up -d --remove-orphans
docker image prune -f --filter "label=org.opencontainers.image.source=https://github.com/dmptrluke/foxtail"
