# Production Deployment

This folder contains everything needed to deploy Foxtail in production.

## Layout

```
deploy/
├── caddy/                # Shared reverse proxy (one per server)
│   ├── compose.yaml
│   └── Caddyfile         # Edit to add site blocks for each stack
├── foxtail/              # App stack template (copy per instance)
│   ├── compose.yaml
│   └── .env.example
└── README.md
```

## Setup

1. Copy `deploy/` to your server
2. Set up the Caddy proxy:

```bash
cd caddy
# Edit Caddyfile to add your domain(s)
docker compose up -d
```

3. Set up the app stack:

```bash
cd foxtail
cp .env.example .env
# Edit .env — fill in required values
```

4. Generate a secret key and add it to `.env`:

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

## Running Multiple Stacks

To run multiple instances (e.g. live + test):

1. Copy the `foxtail/` folder for each instance
2. Set a unique `COMPOSE_PROJECT_NAME` in each `.env` (e.g. `foxtail-live`, `foxtail-test`)
3. Add a site block in `caddy/Caddyfile` for each instance, pointing to `<project-name>-app-1:8000`

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

## Updating

Pull the latest image and restart:

```bash
docker compose pull
docker compose up -d
docker compose exec app django-admin migrate
```
