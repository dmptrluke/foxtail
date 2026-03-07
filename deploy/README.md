# Production Deployment

This folder is a self-contained starting point for deploying Foxtail.

## Setup

1. Copy this entire `deploy/` folder to your server
2. Copy `.env.example` to `.env` and fill in the required values
3. Generate a secret key and add it to `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. Start the stack:

```bash
docker compose up -d
```

5. Run initial migrations:

```bash
docker compose exec foxtail django-admin migrate
```

6. Create a superuser:

```bash
docker compose exec foxtail django-admin createsuperuser
```

## Services

- **caddy** — Reverse proxy with automatic TLS (ports 80, 443)
- **foxtail** — Gunicorn web server (internal port 8000)
- **worker** — RQ background worker (processes async email)
- **db** — PostgreSQL 17
- **redis** — Redis 8 (cache + job queue)

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

Caddy is included as a reverse proxy and automatically obtains TLS certificates via Let's Encrypt. Set `SITE_DOMAIN` in `.env` to your domain name — Caddy uses this to request certificates.

Make sure ports 80 and 443 are open and DNS points to your server before starting the stack.

If you need to use the Cloudflare DNS challenge (e.g. the server isn't publicly reachable on port 80), you'll need to build a custom Caddy image with the `caddy-dns/cloudflare` plugin — see the [caddy-dns/cloudflare](https://github.com/caddy-dns/cloudflare) docs.

## Updating

Pull the latest image and restart:

```bash
docker compose pull
docker compose up -d
docker compose exec foxtail django-admin migrate
```
