#!/bin/bash
set -euo pipefail

cd /opt/foxtail/staging
gh attestation verify oci://ghcr.io/dmptrluke/foxtail:latest -R dmptrluke/foxtail
docker compose pull app worker
docker compose run --rm app django-admin migrate --noinput
docker compose up -d --remove-orphans

# Warm up the app so the first real visitor doesn't eat cold-start latency
# (template compilation, cotton component loading, DB connection pool)
echo "Warming up..."
sleep 2
for path in / /groups/ /events/; do
    docker compose exec -T app python -c \
        "import urllib.request; urllib.request.urlopen('http://localhost:8000${path}')" 2>/dev/null || true
done

docker image prune -f --filter "label=org.opencontainers.image.source=https://github.com/dmptrluke/foxtail"
