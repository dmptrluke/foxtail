"""
Base settings for the foxtail project.
You shouldn't need to edit this file in most cases.

Custom/instance specific settings can be customised using a
<.env> file placed in the project root, or with environment
variables (see https://django-environ.readthedocs.io/)

For Django documentation on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

import logging
from pathlib import Path

from django.contrib.messages import constants as messages

import environ
import pymdownx.emoji
from csp.constants import NONCE, NONE, SELF

logger = logging.getLogger(__name__)

# Build paths inside the project like this: str(BASE_DIR / 'subdir').
SRC_DIR = Path(__file__).resolve(strict=True).parents[1]
BASE_DIR = SRC_DIR.parent

env = environ.Env()
environ.Env.read_env(str(BASE_DIR / '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)
TESTING = env.bool('TESTING', default=False)

SITE_URL = env('SITE_URL').rstrip('/')
SITE_ID = 1

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
INTERNAL_IPS = []
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=False)

ROOT_URLCONF = 'foxtail.urls'

WSGI_APPLICATION = 'foxtail.wsgi.application'

# Application definition
INSTALLED_APPS = [
    'apps.admin.apps.CustomAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.forms',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django.contrib.sitemaps',
    'rules.apps.AutodiscoverRulesConfig',
    'markdownfield',
    'cjswidget',
    'published',
    'structured_data',
    'csp',
    'csp_helpers',
    'apps.core',
    'apps.email',
    'apps.accounts',
    'apps.content',
    'apps.events',
    'apps.directory',
    'apps.blog',
    'apps.contact',
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.github',
    'anymail',
    'mail_templated_simple',
    'taggit',
    'widget_tweaks',
    'allauth.idp',
    'allauth.idp.oidc',
    'django_recaptcha',
    'imagefield',
    'django_rq',
    'django_cleanup.apps.CleanupConfig',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'apps.core.middleware.RequestLoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG,
    }

# Template Engine
# <https://docs.djangoproject.com/en/dev/topics/templates/>

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(SRC_DIR / 'templates').as_posix()],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site',
                'apps.core.context_processors.debug',
                'csp.context_processors.nonce',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# Recognise upstream proxy SSL
# <https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header>
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
# <https://docs.djangoproject.com/en/stable/ref/settings/#databases>

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {'default': env.db('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))}

# Cache
# <https://docs.djangoproject.com/en/stable/topics/cache/#setting-up-the-cache>
CACHES = {'default': env.cache(default='dummycache://')}

# enable the cached session backend
# <https://docs.djangoproject.com/en/stable/topics/http/sessions/#using-cached-sessions>
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# django-rq
# <https://github.com/rq/django-rq>
RQ_ASYNC = env.bool('RQ_ASYNC', default=True)

RQ_QUEUES = {'default': {'USE_REDIS_CACHE': 'default', 'ASYNC': RQ_ASYNC}}

# Authentication
# <https://django-allauth.readthedocs.io/en/latest/>

# django
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'

# allauth
ACCOUNT_ADAPTER = 'apps.accounts.authentication.AccountAdapter'

ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

ACCOUNT_USERNAME_VALIDATORS = 'apps.accounts.validators.username_validators'

ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.SignupForm',
    'reset_password': 'apps.accounts.forms.ResetPasswordForm',  # nosec B105
}

ACCOUNT_RATE_LIMITS = {
    'login': '30/m/ip',
    'login_failed': '10/m/ip,5/5m/key',
    'signup': '20/m/ip',
    'confirm_email': '1/3m/key',
    'reset_password': '20/m/ip,5/m/key',
    'reset_password_from_key': '20/m/ip',
    'change_password': '5/m/user',
    'login_by_code': '5/m/ip',
}

ACCOUNT_LOGIN_BY_CODE_ENABLED = True

# allauth social
SOCIALACCOUNT_ADAPTER = 'apps.accounts.authentication.SocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': ['read:user', 'user:email'],
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    },
}

# allauth-mfa

MFA_SUPPORTED_TYPES = ['recovery_codes', 'totp', 'webauthn']
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

MFA_FORMS = {
    'authenticate': 'allauth.mfa.base.forms.AuthenticateForm',
    'reauthenticate': 'allauth.mfa.base.forms.AuthenticateForm',
    'activate_totp': 'allauth.mfa.totp.forms.ActivateTOTPForm',
    'deactivate_totp': 'allauth.mfa.totp.forms.DeactivateTOTPForm',
    'generate_recovery_codes': 'allauth.mfa.recovery_codes.forms.GenerateRecoveryCodesForm',
}

# OpenID Connect Identity Provider
# <https://docs.allauth.org/en/latest/idp/oidc/index.html>
IDP_OIDC_ADAPTER = 'apps.accounts.adapter.FoxtailOIDCAdapter'
IDP_OIDC_PRIVATE_KEY = env('OIDC_RSA_PRIVATE_KEY', default='')

# Passwords
# <https://docs.djangoproject.com/en/stable/topics/auth/passwords/>
# <https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators>

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ReCAPTCHA
# <https://pypi.org/project/django-recaptcha/>

# I used to pull these from captcha.constants, but it does some annoying stuff
# and seems to run all of the Django system checks if I even touch that module
TEST_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
TEST_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

if DEBUG or TESTING:
    SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

RECAPTCHA_ENABLED = env.bool('RECAPTCHA_ENABLED', default=True)
RECAPTCHA_INVISIBLE = env.bool('RECAPTCHA_INVISIBLE', default=True)

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default=TEST_PUBLIC_KEY)
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default=TEST_PRIVATE_KEY)

# Taggit
# <https://django-taggit.readthedocs.io/en/latest/getting_started.html>
TAGGIT_CASE_INSENSITIVE = True

# Internationalization
# <https://docs.djangoproject.com/en/stable/topics/i18n/>

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Auckland'

USE_I18N = True
USE_TZ = True

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

if DEBUG:
    MESSAGE_LEVEL = 10

# Static files and media (CSS, JavaScript, Images)
# <https://docs.djangoproject.com/en/stable/howto/static-files/>
# <https://docs.djangoproject.com/en/dev/ref/settings/#media-root>

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = [str(BASE_DIR / 'build/static'), str(BASE_DIR / 'assets/static')]

AZURE_MEDIA = env.bool('AZURE_MEDIA', default=False)

if AZURE_MEDIA:
    AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT')
    AZURE_ACCOUNT_KEY = env('AZURE_KEY')
    AZURE_CUSTOM_DOMAIN = env('AZURE_DOMAIN', default=None)
    AZURE_SSL = True

STORAGES = {
    'default': {
        'BACKEND': 'apps.core.storages.MediaAzureStorage'
        if AZURE_MEDIA
        else 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
STATIC_ROOT = str(BASE_DIR / 'static')

if not AZURE_MEDIA:
    MEDIA_ROOT = str(BASE_DIR / 'storage/media')

if TESTING:
    WHITENOISE_AUTOREFRESH = True
    STORAGES['staticfiles'] = {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    }

# Security
# <https://docs.djangoproject.com/en/stable/howto/deployment/checklist/#https>
# <https://docs.djangoproject.com/en/stable/ref/middleware/#x-xss-protection>

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = '__Host-sessionid'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = '__Host-csrftoken'

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

# CSP Headers
# <https://django-csp.readthedocs.io/en/latest/>

ASSET_HOSTS = env.list('ASSET_HOSTS', default=[])

_csp_script_src = [
    "'unsafe-inline'",
    SELF,
    NONCE,
    'https://www.google.com/recaptcha/',
    'https://www.gstatic.com/recaptcha/',
] + ASSET_HOSTS

# we don't use strict-dynamic in debug because it breaks django-debug-toolbar
if not DEBUG:
    _csp_script_src += ["'strict-dynamic'"]

CONTENT_SECURITY_POLICY = {
    # admin is excluded because Django admin requires 'unsafe-eval' for JSONField widgets
    'EXCLUDE_URL_PREFIXES': ['/admin'],
    'DIRECTIVES': {
        'default-src': [SELF],
        'script-src': _csp_script_src,
        'style-src': ["'unsafe-inline'", SELF, NONCE] + ASSET_HOSTS,
        'frame-src': [
            'https://www.google.com/recaptcha/',
            'https://www.youtube.com',
            'https://www.youtube-nocookie.com',
        ],
        'font-src': [SELF, 'data:'] + ASSET_HOSTS,
        'img-src': [SELF, 'data:'] + ASSET_HOSTS,
        'object-src': [NONE],
        'connect-src': [SELF, 'https://sentry.io'],
        'base-uri': [NONE],
        'frame-ancestors': [NONE],
        'form-action': [SELF],
        'upgrade-insecure-requests': True,
        'report-uri': env('CSP_REPORT_URI', default=None),
    },
}

# Sentry.io
# <https://docs.sentry.io/platforms/python/django/>

SENTRY_ENABLED = env.bool('SENTRY_ENABLED', default=False)

if SENTRY_ENABLED:
    SENTRY_DSN = env('SENTRY_DSN')

    from urllib.parse import urlparse

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    _vars = {
        'dsn': SENTRY_DSN,
        'send_default_pii': env.bool('SENTRY_PII', default=False),
        'integrations': [DjangoIntegration(), RedisIntegration()],
    }

    # attach environment
    SENTRY_ENVIRONMENT = env('SENTRY_ENVIRONMENT', default='')
    if SENTRY_ENVIRONMENT:
        _vars['environment'] = SENTRY_ENVIRONMENT

    # attach version
    SENTRY_RELEASE = env('SENTRY_RELEASE', default='')
    if SENTRY_RELEASE:
        _vars['release'] = SENTRY_RELEASE

    # set CSP report URI
    if env.bool('SENTRY_CSP', default=False):
        _csp_report_uri = 'https://sentry.io/api/{}/security/?sentry_key={}'.format(
            urlparse(SENTRY_DSN).path.strip('/'), urlparse(SENTRY_DSN).username
        )

        if _vars.get('release'):
            _csp_report_uri += f'&sentry_release={_vars["release"]}'

        CONTENT_SECURITY_POLICY['DIRECTIVES']['report-uri'] = _csp_report_uri

    sentry_sdk.init(**_vars)

# Logging
# <https://docs.djangoproject.com/en/dev/ref/settings/#logging>
# <https://docs.djangoproject.com/en/dev/topics/logging>
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] ['
            + env('SERVICE_NAME', default='app')
            + '/%(process)d] [%(levelname)s] (%(module)s) %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'access': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'access': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'access',
        },
    },
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'sentry_sdk': {'level': 'ERROR', 'handlers': ['console']},
        'azure': {'level': 'WARNING'},
        'django.request': {'level': 'ERROR', 'handlers': ['console'], 'propagate': False},
        'apps.core.access': {'level': 'INFO', 'handlers': ['access'], 'propagate': False},
    },
}

# Email
# <https://docs.djangoproject.com/en/stable/topics/email/>
# <https://anymail.readthedocs.io/en/stable/>
DEFAULT_FROM_EMAIL = env('EMAIL_FROM_USER', default='webmaster@localhost')
SERVER_EMAIL = env('EMAIL_FROM_SYSTEM', default='root@localhost')

if 'MAILGUN_API_KEY' in env:
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    ANYMAIL_MAILGUN_API_KEY = env('MAILGUN_API_KEY')

    if 'MAILGUN_SENDER_DOMAIN' in env:
        ANYMAIL_MAILGUN_SENDER_DOMAIN = env('MAILGUN_SENDER_DOMAIN')

else:
    EMAIL_CONFIG = env.email_url('EMAIL_URL', default='consolemail://')
    vars().update(EMAIL_CONFIG)

EMAIL_REAL_BACKEND = EMAIL_BACKEND
EMAIL_BACKEND = 'apps.email.engine.AsyncEmailBackend'

# django-imagefield
# <https://django-imagefield.readthedocs.io/en/latest/>
IMAGEFIELD_BACKEND = 'vips'
IMAGEFIELD_AUTOGENERATE = False
IMAGEFIELD_FORMATS = {
    'accounts.user.avatar': {
        'small': ['default', ('crop', (80, 80))],
        'small_2x': ['default', ('crop', (160, 160))],
        'medium': ['default', ('crop', (160, 160))],
        'medium_2x': ['default', ('crop', (320, 320))],
        'large': ['default', ('crop', (400, 400))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'accounts.clientmetadata.logo': {
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'foxtail_blog.author.avatar': {
        'small': ['default', ('crop', (80, 80))],
        'small_2x': ['default', ('crop', (160, 160))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'foxtail_blog.post.image': {
        'card': ['default', ('crop', (800, 400))],
        'card_2x': ['default', ('crop', (1600, 800))],
        'featured': ['default', ('crop', (700, 350))],
        'featured_2x': ['default', ('crop', (1400, 700))],
        'banner': ['default', ('crop', (1440, 443))],
        'banner_2x': ['default', ('crop', (2880, 886))],
        'banner_mobile': ['default', ('crop', (768, 1024))],
        'banner_mobile_2x': ['default', ('crop', (1536, 2048))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'events.event.image': {
        'card': ['default', ('crop', (400, 200))],
        'card_2x': ['default', ('crop', (800, 400))],
        'featured': ['default', ('crop', (700, 350))],
        'featured_2x': ['default', ('crop', (1400, 700))],
        'banner': ['default', ('crop', (1440, 350))],
        'banner_2x': ['default', ('crop', (2880, 700))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
}

# Markdown
MARKDOWN_EXTENSIONS = [
    'pymdownx.smartsymbols',
    'pymdownx.betterem',
    'pymdownx.tilde',
    'pymdownx.caret',
    'pymdownx.emoji',
    'sane_lists',
    'def_list',
    'nl2br',
    'abbr',
    'smarty',
]

MARKDOWN_EXTENSION_CONFIGS = {'pymdownx.emoji': {'emoji_generator': pymdownx.emoji.to_alt}}

MARKDOWN_LINKIFY_BLACKLIST = []

# robots.txt
ROBOTS_ALLOWED = env.bool('ROBOTS_ALLOWED', default=True)

# Django Structured Data
# <https://github.com/dmptrluke/django-structured-data>
DEFAULT_STRUCTURED_DATA = {
    'publisher': {
        '@id': 'https://furry.nz/#organization',
    }
}


# Blog
BLOG_COMMENTS = True

# Contact
CONTACT_EMAILS = env.list('CONTACT_EMAILS')

# Foxtail
DIRECTORY_ENABLED = env.bool('DIRECTORY_ENABLED', default=False)
MAPBOX_ACCESS_TOKEN = env('MAPBOX_ACCESS_TOKEN', default='')
