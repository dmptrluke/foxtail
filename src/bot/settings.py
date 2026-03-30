"""Minimal Django settings for the bot process. Database and model loading only."""

import environ

env = environ.Env()
env.read_env('.env')

SECRET_KEY = 'bot-process-not-serving-http'  # noqa: S105
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASES = {
    'default': env.db(default='postgres://foxtail:foxtail@db/foxtail'),
}
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'apps.accounts',
    'apps.telegram',
]

MIDDLEWARE = []

SILENCED_SYSTEM_CHECKS = [
    'allauth.account.W002',  # AccountMiddleware not needed (bot has no HTTP stack)
]

SITE_ID = 1

USE_TZ = True
TIME_ZONE = 'Pacific/Auckland'
AUTH_USER_MODEL = 'accounts.User'

REDIS_URL = env.str('CACHE_URL', default='redis://redis/1')

SITE_URL = env('SITE_URL', default='https://furry.nz')
TELEGRAM_WEBHOOK_SECRET = env('TELEGRAM_WEBHOOK_SECRET', default='')
