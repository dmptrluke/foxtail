# Dependencies

FROM node:22-slim AS assets
ARG BUILD_MODE=production
ENV NODE_ENV=$BUILD_MODE

WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY vite.config.mjs ./
COPY assets/ ./assets/
RUN npm run-script build-${BUILD_MODE}

FROM python:3.13-slim AS deps
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src" \
    DJANGO_SETTINGS_MODULE=foxtail.settings

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /usr/local/bin/uv

RUN groupadd -r abc -g 5678 && useradd --no-log-init -u 5678 -r -g abc abc

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 libvips

RUN mkdir -p /app/static /app/storage/media \
    && chown -R abc:abc /app/static /app/storage

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Application

FROM deps AS app

ARG GIT_SHA
ENV SENTRY_RELEASE=$GIT_SHA

RUN rm /usr/local/bin/uv

COPY --from=assets /app/build ./build
COPY --chown=abc:abc . .

USER abc

RUN SECRET_KEY=build-placeholder SITE_URL=http://localhost CONTACT_EMAILS=noop@localhost \
    django-admin collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/dev/shm", "--forwarded-allow-ips", "*", "-k", "gthread", "--threads", "4", "foxtail.wsgi:application"]
