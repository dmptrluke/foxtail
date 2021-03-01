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

COPY --from=0 /app/assets/dist /app/assets/dist
COPY --from=0 /app/assets/webpack-stats.json /app/assets/webpack-stats.json
COPY [".", "./"]

EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=foxtail.settings

RUN mkdir /app/static

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
