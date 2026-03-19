# foxtail
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmptrluke/foxtail/build.yml?branch=master&style=flat&label=build&link=https%3A%2F%2Fgithub.com%2Fdmptrluke%2Ffoxtail%2Factions%2Fworkflows%2Fbuild.yml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmptrluke/foxtail/build.yml?branch=master&style=flat&label=test&link=https%3A%2F%2Fgithub.com%2Fdmptrluke%2Ffoxtail%2Factions%2Fworkflows%2Ftest.yml)
![Codecov](https://img.shields.io/codecov/c/github/dmptrluke/foxtail)

The code behind furry.nz - a login provider and general community website for the NZ furry community.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL and Redis)
- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22+ with npm

### Configuration

Create a `.env` file in the project root with the following minimal configuration:

```
DEBUG=True
SECRET_KEY=REPLACEME
SITE_URL=http://127.0.0.1:8000
CONTACT_EMAILS=admin@example.com
DATABASE_URL=postgres://foxtail:foxtail@localhost/foxtail
CACHE_URL=redis://localhost/1
HUEY_IMMEDIATE=True
VITE_DEV_MODE=True
```

### Setup

```bash
# Start PostgreSQL and Redis
docker compose up -d

# Install dependencies
uv sync --group dev --group test
npm install

# Run migrations
uv run python src/manage.py migrate
```

### Running

```bash
# Django dev server
uv run python src/manage.py runserver

# Vite dev server (separate terminal, for HMR + asset serving)
npm run dev
```

Access foxtail at <http://127.0.0.1:8000/>.

### Running the tests

This project uses `pytest` and `pytest-django` for automated code testing.

```bash
uv run pytest src/apps/ -v
```

### Production-like local testing

To test the full production Docker image locally (gunicorn, collectstatic, WhiteNoise):

```bash
docker compose -f compose.yaml -f compose.prod.yaml up --build
```

## Deployment

See [deploy/](deploy/) for a production-ready compose file and configuration template.

## License

```text
Copyright (c) Luke Rogers 2019-2026

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

This Source Code Form is "Incompatible With Secondary Licenses", as
defined by the Mozilla Public License, v. 2.0.
```

## Built With

- [Django](https://www.djangoproject.com/) - The backend, the star of the whole show.
- [Bootstrap](https://getbootstrap.com/) - Front-end CSS framework.
- [Vite](https://vite.dev/) - Front-end bundling and asset management.
- [Huey](https://huey.readthedocs.io/) - Job queueing and background tasks.

## Thanks To

- [BrowserStack](https://www.browserstack.com/open-source) - For providing web testing and visual regression testing through their open source program.
- [Sentry](https://sentry.io/for/open-source/) - For providing error and performance monitoring through their open source program.
