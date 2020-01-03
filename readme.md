# foxtail [![CircleCI](https://github.com/dmptrluke/foxtail/workflows/Test/badge.svg)](https://github.com/dmptrluke/foxtail/actions)

The code behind furry.nz - a  login provider and general community website for the NZ furry community.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Requirements

The foxtail project requires at least **Python 3.6** and a recent-*ish* version of node.js.
We recommend you run all of the below commands in a dedicated [virtual environment](https://docs.python.org/3/library/venv.html)
to keep things tidy.


### Prerequisites

To get started, you'll need to install the Python requirements. You can do this with the following command.

```
pip install -r requirements.txt
```

And, the node.js requirements.

```
npm install
```


### Building Assets

When any files in the `assets` folder are updated, you'll need to re-build the assets. You will also need to
do this when you first install the project.

```
npm run-script build-dev
```

During development, you can also use `run-script watch` to enable live reloads.
```
npm run-script build-dev
```

### Configuration

A number of basic configuration options are required for foxtail to function. These can be
set using environment varibles, or placed in a `.env` file in the project root.

Included below is an example of a minimal `.env` file to be used for local development.

```
DEBUG=True
SITE_URL=http://127.0.0.1:8000
INTERNAL_IPS=127.0.0.1

# replace this with your own key!
SECRET_KEY=REPLACEME

# recaptcha test keys
RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe

```

To generate a new secret key, open a Python shell and run the following commands.

```py
from foxtail.utils import get_random_secret_key
get_random_secret_key()
```

### Installing

First, create the foxtail database.

```
./manage.py migrate
```

And then generate an RSA key.

```
./manage.py creatersakey
```

### Running
Now your development environment is ready, simply run the below to start it up.
```
./manage.py runserver
```

You should then be able to access foxtail at http://127.0.0.1:8000/.

## Running the tests

This project uses `pytest`, `pytest-django`, and `selenium` for automated code testing.

To install the dependencies for testing, use the following command. You may also need to follow
[additional steps](https://selenium-python.readthedocs.io/installation.html) to get the
selenium test suites to run.
```
pip install -r tests/requirements.txt
```



You can then use the following command to run the automated test suites.

```
pytest
```


## Deployment

The instructions in this section will be more technical than the section above. A decent amount of
knowledge about Linux administration is assumed.

There are four main components to deploying this project in a real production environment.

* Starting and managing foxtail with Gunicorn
* Using Redis as a cache.
* Using PostgreSQL for database.
* Configuring and enabling Django-RQ

You will also need to follow most of the steps listed above in *Getting Started*, with some obvious alterations -

* `npm run-script build` instead of `npm run-script build-dev`
* `DEBUG=FALSE` in .env

### Gunicorn
Following the Gunicorn documentation is the simplest way to get this working.
The base command you'll want to use to run the project will be `gunicorn foxtail.wsgi:application`.

This does not include any additional flags you may need to set, such as `-w 3` to set the number of workers, or any
 web server/socket configuration. **You will have to set those up yourself**. See the below link
 for information.

http://docs.gunicorn.org/en/latest/deploy.html

### Redis
Install and configure Redis according to instructions for your distribution, then add the following
line in your `.env` file.

For an unauthenticated Redis install (this is the default):

```
CACHE_URL=redis://HOSTNAME:PORT/1
```

For an authenticated Redis install:
```
CACHE_URL=redis://:PASSWORD@HOST:PORT/1
```

Other caching solutions can be used (like memcached), but this will break Django-RQ, which relies on
a working Redis configuration.


## Built With

* [Bootstrap](https://getbootstrap.com/) - Frontend CSS framework
* [Django](https://www.djangoproject.com/) - Backend
