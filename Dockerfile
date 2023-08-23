FROM node:18
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

WORKDIR /app

COPY ["requirements.txt", "./"]
RUN pip install -r requirements.txt

COPY --from=0 /app/assets/generated /app/assets/generated
COPY [".", "./"]

RUN django-admin collectstatic --noinput

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foxtail.wsgi:application"]
