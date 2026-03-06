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

- **foxtail** — Gunicorn web server on port 8000
- **worker** — RQ background worker (processes async email)
- **db** — PostgreSQL 16
- **redis** — Redis 7 (cache + job queue)

## OIDC Signing Key

Foxtail can act as an OpenID Connect identity provider, which requires an RSA signing key. Generate one with:

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt
```

Add the output to your `.env` file as `OIDC_RSA_PRIVATE_KEY`, wrapped in quotes with `\n` for newlines:

```
OIDC_RSA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADA...\n-----END PRIVATE KEY-----"
```

## Reverse Proxy

The app listens on port 8000. Put a web server in front of it to handle TLS termination. Set `USE_X_FORWARDED_HOST=true` in `.env` if your proxy sets that header.

## Updating

Pull the latest image and restart:

```bash
docker compose pull
docker compose up -d
docker compose exec foxtail django-admin migrate
```
