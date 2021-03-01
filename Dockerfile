FROM node:10
ENV MODE=production
ENV NODE_ENV=${MODE}

WORKDIR /app
COPY ["package.json", "package-lock.json", "./"]
RUN npm ci

COPY ["webpack.*", "./"]
COPY ["assets", "./assets/"]
RUN npm run-script build-${MODE}

FROM python:3.9

WORKDIR /app
COPY ["requirements.txt", "./"]

RUN pip install -r requirements.txt

COPY --from=0 /app/assets/generated /app/assets/generated
COPY [".", "./"]

EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=foxtail.settings
ENV GUNICORN_WORKERS=2

RUN mkdir /app/static

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
