# foxtail
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmptrluke/foxtail/build.yml?branch=master&style=flat&label=build&link=https%3A%2F%2Fgithub.com%2Fdmptrluke%2Ffoxtail%2Factions%2Fworkflows%2Fbuild.yml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dmptrluke/foxtail/build.yml?branch=master&style=flat&label=test&link=https%3A%2F%2Fgithub.com%2Fdmptrluke%2Ffoxtail%2Factions%2Fworkflows%2Ftest.yml)
![Codecov](https://img.shields.io/codecov/c/github/dmptrluke/foxtail)




The code behind furry.nz - a login provider and general community website for the NZ furry community.

## Getting Started

This project is designed to be run with Docker. You'll need [Docker](https://docs.docker.com/get-docker/) installed.

### Configuration

Create a `.env` file in the project root with the following minimal configuration:

```
DEBUG=True
SITE_URL=http://127.0.0.1:8000
SECRET_KEY=REPLACEME
CONTACT_EMAILS=admin@example.com
```

### Running

Start the application with Docker Compose:

```
docker compose up --build
```

This will start the application along with PostgreSQL and Redis. Migrations run automatically on startup.
You can access foxtail at http://127.0.0.1:8000/.

To run migrations manually:

```bash
docker compose run --rm foxtail django-admin migrate
```

### Running the tests

This project uses `pytest` and `pytest-django` for automated code testing.

To run the test suite in Docker:

```
docker compose run --rm test
```

## Deployment

See [deploy/](deploy/) for a production-ready compose file and configuration template.

## License
```
Copyright (c) Luke Rogers 2019-2026

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

This Source Code Form is "Incompatible With Secondary Licenses", as
defined by the Mozilla Public License, v. 2.0.
```

## Built With

* [Django](https://www.djangoproject.com/) - The backend, the star of the whole show.
* [Bootstrap](https://getbootstrap.com/) - Front-end CSS framework.
* [Vite](https://vite.dev/) - Front-end bundling and asset management.
* [RQ (Redis Queue)](https://python-rq.org/) - Job queueing and background tasks.


## Thanks To

* [JetBrains](https://www.jetbrains.com/?from=furry.nz) - For providing software licenses for PyCharm Professional through their open source program.
* [BrowserStack](https://www.browserstack.com/open-source) - For providing free desktop and mobile web testing
through their open source program.
