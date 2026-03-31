# Assets

FROM dhi.io/node:22-debian13-dev AS assets
ARG BUILD_MODE=production
ENV NODE_ENV=$BUILD_MODE

WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY vite.config.mjs ./
COPY assets/ ./assets/
RUN npm run-script build-${BUILD_MODE}

# Dependencies

FROM dhi.io/python:3.14-debian13-dev AS deps
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Collect static files

FROM deps AS builder

ARG GIT_SHA
ARG RELEASE_VERSION
ENV GIT_SHA=$GIT_SHA \
    RELEASE_VERSION=$RELEASE_VERSION \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    DJANGO_SETTINGS_MODULE=foxtail.settings

COPY --from=assets /app/build ./build
COPY . .
RUN SECRET_KEY=build-placeholder SITE_URL=http://localhost CONTACT_EMAILS=noop@localhost \
    django-admin collectstatic --noinput
RUN mkdir -p /app/storage/media

# Application (distroless)

FROM dhi.io/python:3.14-debian13 AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src" \
    DJANGO_SETTINGS_MODULE=foxtail.settings \
    PATH="/app/.venv/bin:/opt/python/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/dmptrluke/healthcheck@sha256:3e9025c3550d94f35f1c565f8e71f89c9492fa4e79e440292ab776a144c460bb /healthcheck /usr/local/bin/healthcheck
COPY --from=deps /app/.venv /app/.venv
COPY --from=builder /app/build ./build
COPY --from=builder /app/static ./static
COPY --from=builder --chown=65532:65532 /app/storage ./storage
COPY . .

ARG GIT_SHA
ARG RELEASE_VERSION
ENV GIT_SHA=$GIT_SHA
ENV RELEASE_VERSION=$RELEASE_VERSION

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/dev/shm", "--forwarded-allow-ips", "*", "-k", "gthread", "--threads", "4", "foxtail.wsgi:application"]
