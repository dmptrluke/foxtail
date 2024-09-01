FROM node:20
ARG BUILD_MODE=production
ENV NODE_ENV=$BUILD_MODE

WORKDIR /app
COPY ["package.json", "package-lock.json", "./"]
RUN npm ci

COPY ["webpack.*", "./"]
COPY ["assets", "./assets/"]
RUN npm run-script build-${BUILD_MODE}

FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=foxtail.settings
ENV GUNICORN_WORKERS=2

# add a user/group for our app to run under
RUN groupadd -r abc -g 5678 && useradd --no-log-init -u 5678 -r -g abc abc

WORKDIR /app

COPY ["requirements.txt", "./"]
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=0 /app/assets/generated /app/assets/generated
COPY [".", "./"]

# Ensures file ownership is correct
RUN chown -R abc /app
USER abc

EXPOSE 8000
CMD django-admin collectstatic --noinput;gunicorn --bind 0.0.0.0:8000 foxtail.wsgi:application
