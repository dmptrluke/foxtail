## Deployment

The instructions in this document will be more technical than the readme. A decent amount of
knowledge about Linux administration is assumed.

There are four main components to deploying this project in a real production environment.

* Starting and managing foxtail with Gunicorn
* Using Redis as a cache.
* Using PostgreSQL for database.
* Configuring and enabling Django-RQ

You will also need to follow most of the steps listed in *Getting Started*, with some obvious alterations -

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
