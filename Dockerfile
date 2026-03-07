# Dependencies

FROM node:22-slim AS assets
ARG BUILD_MODE=production
ENV NODE_ENV=$BUILD_MODE

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY vite.config.mjs ./
COPY assets/ ./assets/
RUN npm run-script build-${BUILD_MODE}

FROM python:3.13-slim AS deps
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src" \
    DJANGO_SETTINGS_MODULE=foxtail.settings

WORKDIR /app

RUN groupadd -r abc -g 5678 && useradd --no-log-init -u 5678 -r -g abc abc

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 libvips \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/static /app/storage/media \
    && chown -R abc:abc /app/static /app/storage

COPY requirements/base.txt ./requirements/base.txt
RUN pip install --no-cache-dir -r requirements/base.txt

FROM deps AS dev-deps

COPY requirements/dev.txt ./requirements/dev.txt
RUN pip install --no-cache-dir -r requirements/dev.txt

FROM dev-deps AS test-deps

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget gnupg2 \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/test.txt ./requirements/test.txt
RUN pip install --no-cache-dir -r requirements/test.txt

RUN mkdir -p /home/abc/.cache && chown -R abc:abc /home/abc

# Applications

FROM deps AS app

COPY --from=assets /app/build ./build
COPY --chown=abc:abc . .

USER abc

RUN SECRET_KEY=build-placeholder SITE_URL=http://localhost CONTACT_EMAILS=noop@localhost \
    django-admin collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/dev/shm", "--forwarded-allow-ips", "*", "foxtail.wsgi:application"]

FROM dev-deps AS dev

COPY --from=assets /app/build ./build
COPY --chown=abc:abc . .

USER abc

FROM test-deps AS test

COPY --from=assets /app/build ./build
COPY --chown=abc:abc . .

USER abc

CMD ["python", "-m", "pytest"]
