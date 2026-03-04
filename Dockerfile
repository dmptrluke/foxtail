# Stage 1: Build frontend assets
FROM node:22-slim AS assets
ARG BUILD_MODE=production
ENV NODE_ENV=$BUILD_MODE

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY webpack.* ./
COPY assets/ ./assets/
RUN npm run-script build-${BUILD_MODE}

# Stage 2: Application
FROM python:3.13-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    DJANGO_SETTINGS_MODULE=foxtail.settings \
    GUNICORN_WORKERS=2

WORKDIR /app

RUN groupadd -r abc -g 5678 && useradd --no-log-init -u 5678 -r -g abc abc

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=assets /app/assets/generated ./assets/generated
COPY --chown=abc:abc . .

USER abc

EXPOSE 8000
CMD ["sh", "-c", "django-admin collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 foxtail.wsgi:application"]

# Stage 3: Test runner (includes Chrome for Selenium tests)
FROM app AS test

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget gnupg2 \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY tests/requirements.txt ./tests/requirements.txt
RUN pip install --no-cache-dir -r tests/requirements.txt

USER abc

CMD ["python", "-m", "pytest"]
