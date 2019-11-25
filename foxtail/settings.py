"""
Base settings for the foxtail project.
You shouldn't need to edit this file in most cases.

Custom/instance specific settings can be customised using a
<.env> file placed in the project root, or with environment
variables (see https://django-environ.readthedocs.io/)

For Django documentation on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import logging
import os

import environ
import pymdownx.emoji
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

SITE_URL = env('SITE_URL')
SITE_ID = 1

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
INTERNAL_IPS = env.list('INTERNAL_IPS', default=[])

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
    'django.contrib.humanize',
    'django.contrib.postgres',
    'apps.core',
    'apps.accounts',
    'apps.content',
    'apps.events',
    'apps.directory',
    'foxtail_blog',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.github',

    # Configure the django-otp package.
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',

    # Enable two-factor auth.
    'allauth_2fa',
    'taggit',
    'adminsortable2',
    'guardian',
    'webpack_loader',
    'crispy_forms',
    'oidc_provider',
    'captcha',
    'versatileimagefield',

]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Template Engine
# <https://docs.djangoproject.com/en/dev/topics/templates/>

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'apps.core.context_processors.site',
                'csp.context_processors.nonce'
            ],
        },
    },
]

# Message Tags
# <https://docs.djangoproject.com/en/2.2/ref/contrib/messages/#message-tags>
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Recognise upstream proxy SSL
# <https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header>
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security
# <https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/#https>
# <https://docs.djangoproject.com/en/2.2/ref/middleware/#x-xss-protection>

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = '__Host-sessionid'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = '__Host-csrftoken'

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'

X_FRAME_OPTIONS = 'DENY'

# CSP Headers
# <https://django-csp.readthedocs.io/en/latest/>

CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
CSP_UPGRADE_INSECURE_REQUESTS = True

CSP_DEFAULT_SRC = ["'self'"]

CSP_REPORT_URI = env('CSP_REPORT_URI', default=None)

CSP_SCRIPT_SRC = ["'unsafe-inline'", "'self'", 'https://www.google.com/recaptcha/',
                  'https://www.gstatic.com/recaptcha/']
CSP_STYLE_SRC = ["'unsafe-inline'", 'fonts.googleapis.com', "'self'"]
CSP_FRAME_SRC = ['https://www.google.com/recaptcha/']
CSP_FONT_SRC = ["'self'", 'data:', 'fonts.gstatic.com']
CSP_IMG_SRC = ["'self'", 'data:', 'ui-avatars.com', 'www.gravatar.com']
CSP_OBJECT_SRC = ["'none'"]

CSP_BASE_URI = ["'none'"]
CSP_FRAME_ANCESTORS = ["'none'"]
CSP_FORM_ACTION = ["'self'"] + env.list('CSP_FORM_ACTION', default=[])

CSP_EXCLUDE_URL_PREFIXES = ('/admin',)

# we don't use strict-dynamic in debug because it breaks django-debug-toolbar
if not DEBUG:
    CSP_SCRIPT_SRC += ["'strict-dynamic'"]

# Database
# <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>
# <https://pypi.org/project/dj-database-url/>

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    )
}

# Cache
# <https://docs.djangoproject.com/en/2.2/topics/cache/#setting-up-the-cache>
CACHE_URL = env.cache(default='dummycache://')
CACHES = {
    'default': CACHE_URL
}

# enable the cached session backend
# <https://docs.djangoproject.com/en/2.2/topics/http/sessions/#using-cached-sessions>
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Authentication
# <https://django-allauth.readthedocs.io/en/latest/>

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend'
]

ACCOUNT_ADAPTER = 'apps.accounts.authentication.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.accounts.authentication.SocialAccountAdapter'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# custom validator allows spaces in usernames
ACCOUNT_USERNAME_VALIDATORS = 'apps.accounts.validators.username_validators'

LOGIN_REDIRECT_URL = '/'

ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.SignupForm',
    'reset_password': 'apps.accounts.forms.ResetPasswordForm',
    'login': 'apps.accounts.forms.LoginForm'
}

ALLAUTH_2FA_ALWAYS_REVEAL_BACKUP_TOKENS = False

SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'read:user',
            'user:email'
        ],
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Passwords
# <https://docs.djangoproject.com/en/2.2/topics/auth/passwords/>

# <https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators>
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

# OIDC Server
# <https://django-oidc-provider.readthedocs.io/en/latest/>
OIDC_SESSION_MANAGEMENT_ENABLE = True
OIDC_USERINFO = 'apps.accounts.claims.userinfo'

# ReCAPTCHA
# <https://pypi.org/project/django-recaptcha/>
RECAPTCHA_ENABLED = True
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')

# Internationalization
# <https://docs.djangoproject.com/en/2.2/topics/i18n/>

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Auckland'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Static files (CSS, JavaScript, Images)
# <https://docs.djangoproject.com/en/2.2/howto/static-files/>

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_out')

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = [
    ("bundles", os.path.join(BASE_DIR, 'assets/bundles')),
    os.path.join(BASE_DIR, 'assets/static')
]

# Media
# <https://docs.djangoproject.com/en/dev/ref/settings/#media-root>
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# if using the debug server, set the correct MIME type for .js files
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/javascript", ".js", True)

# Webpack Loader
# <https://github.com/owais/django-webpack-loader>
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Sentry.io
# <https://docs.sentry.io/platforms/python/django/>

SENTRY_ENABLED = env.bool('SENTRY_ENABLED', default=False)

if SENTRY_ENABLED:
    SENTRY_DSN = env('SENTRY_DSN')

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    _vars = {
        'dsn': SENTRY_DSN,
        'send_default_pii': env.bool('SENTRY_PII', default=False),
        'integrations': [DjangoIntegration()]
    }

    SENTRY_ENVIRONMENT = env('sentry_environment', default=False)

    if SENTRY_ENVIRONMENT:
        _vars['environment'] = SENTRY_ENVIRONMENT

    if env.bool('SENTRY_GIT', default=False):
        import git

        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        _vars['release'] = sha

    sentry_sdk.init(**_vars)

# Logging
# <https://docs.djangoproject.com/en/dev/ref/settings/#logging>
# <https://docs.djangoproject.com/en/dev/topics/logging>
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Email
# <https://docs.djangoproject.com/en/2.2/topics/email/>

try:
    DEFAULT_FROM_EMAIL = env('EMAIL_FROM_USER')
    SERVER_EMAIL = env('EMAIL_FROM_SYSTEM')

    EMAIL_CONFIG = env.email_url('EMAIL_URL')
    vars().update(EMAIL_CONFIG)

except ImproperlyConfigured as e:
    if DEBUG:
        logger.warning('Foxtail is in DEBUG mode with missing email credentials. '
                       'Enabling console email backend!')
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        raise e

# Crispy Forms
# <https://django-crispy-forms.readthedocs.io/en/latest/>
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# VersatileImageField
# <https://django-versatileimagefield.readthedocs.io/en/latest/installation.html#versatileimagefield-settings>
VERSATILEIMAGEFIELD_SETTINGS = {
    'jpeg_resize_quality': 80
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
    'smarty'
]

MARKDOWN_EXTENSION_CONFIGS = {
    'pymdownx.emoji': {
        'emoji_generator': pymdownx.emoji.to_alt
    }
}

# Heroku Support
if env.bool('USING_HEROKU', default=False):
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
    CACHES = {
        'default': {
            'BACKEND': 'django_bmemcached.memcached.BMemcached'
        }
    }

    import django_heroku
    django_heroku.settings(locals())
