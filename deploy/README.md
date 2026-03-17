# Production Deployment

This folder contains everything needed to deploy Foxtail in production.

## Layout

```
deploy/
├── caddy/                # Shared reverse proxy (one per server)
│   ├── compose.yaml
│   └── Caddyfile         # Edit to add site blocks for each stack
├── prod/                 # Production stack
│   ├── compose.yaml
│   └── .env.example
├── staging/              # Staging stack
│   ├── compose.yaml
│   └── .env.example
├── scripts/              # Deploy scripts (called by CI)
│   ├── deploy-staging.sh
│   └── deploy-prod.sh
└── README.md
```

## Setup

1. Copy `deploy/` to `/opt/foxtail/` on your server. All paths below assume this location.

2. Set up the Caddy proxy:

```bash
cd /opt/foxtail/caddy
# Edit Caddyfile to add your domain(s)
docker compose up -d
```

For each stack (`prod/` and `staging/`), run steps 3-6:

3. Configure the environment:

```bash
cd /opt/foxtail/prod  # or /opt/foxtail/staging
cp .env.example .env
# Edit .env -- fill in required values
```

4. Generate a secret key and add it to `.env` (use a different key per stack):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

5. Start the stack:

```bash
docker compose up -d
```

6. Run initial migrations and create a superuser:

```bash
docker compose exec app django-admin migrate
docker compose exec app django-admin createsuperuser
```

## Services

Each app stack includes:

- **app** — Gunicorn web server (internal port 8000)
- **worker** — Huey background worker
- **db** — PostgreSQL 17
- **redis** — Redis 8 (cache + job queue)

The shared Caddy proxy handles TLS and routing (ports 80, 443).

## OIDC Signing Key

Foxtail can act as an OpenID Connect identity provider, which requires an RSA signing key. Generate one with:

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt
```

Add the output to your `.env` file as `OIDC_RSA_PRIVATE_KEY`, wrapped in quotes with `\n` for newlines:

```
OIDC_RSA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADA...\n-----END PRIVATE KEY-----"
```

## TLS / Caddy

Caddy automatically obtains TLS certificates via Let's Encrypt. Make sure ports 80 and 443 are open and DNS points to your server before starting.

If you need to use the Cloudflare DNS challenge (e.g. the server isn't publicly reachable on port 80), you'll need to build a custom Caddy image with the `caddy-dns/cloudflare` plugin — see the [caddy-dns/cloudflare](https://github.com/caddy-dns/cloudflare) docs.

## Continuous Deployment

Foxtail has a automated release process.

Pushes to `master` automatically build a Docker image, deploy to staging, then wait
for manual approval before deploying to production. Sentry releases are created after
each deploy.

```
push to master
  -> build image (cloud runner, pushes to ghcr.io with SHA tag)
  -> deploy to staging (self-hosted runner)
  -> create Sentry release (staging)
  -> deploy to production (requires approval in GitHub UI)
  -> create Sentry release (production)
```

The pipeline uses a sandboxed GitHub Actions self-hosted runner. Demo scripts are included, but full deployment details are not included in this repository.
