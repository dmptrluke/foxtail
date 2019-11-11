"""
Base settings for the foxtail project.
You shouldn't need to edit this file in most cases.

Custom/instance specific settings can be customised using a
<settings.ini> or <.env> file placed in the project root, or with
environment variables (see https://pypi.org/project/python-decouple/)

For Django documentation on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import logging
import os

import pymdownx.emoji
from decouple import config, Csv, UndefinedValueError
from dj_database_url import parse as db_url
from django.contrib.messages import constants as messages

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

SITE_URL = config('SITE_URL')
SITE_ID = 1

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())
INTERNAL_IPS = config('INTERNAL_IPS', default="", cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'apps.core.apps.CoreConfig',
    'apps.blog.apps.BlogConfig',
    'apps.accounts.apps.UserConfig',
    'apps.content.apps.ContentConfig',
    'apps.directory.apps.DirectoryConfig',
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
    'taggit_templatetags2',
    'adminsortable2',
    'guardian',
    'markdownx',
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
    'csp.middleware.CSPMiddleware'
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'foxtail.urls'

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

WSGI_APPLICATION = 'foxtail.wsgi.application'

# Recognise upstream proxy SSL
# <https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header>
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security
# <https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/#https>
# <https://docs.djangoproject.com/en/2.2/ref/middleware/#x-xss-protection>

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'

X_FRAME_OPTIONS = 'DENY'

# CSP Headers
# <https://django-csp.readthedocs.io/en/latest/>

CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
CSP_UPGRADE_INSECURE_REQUESTS = True

CSP_SCRIPT_SRC = ["'unsafe-inline'", "'self'"]
CSP_STYLE_SRC = ["'unsafe-inline'", "'self'"]
CSP_IMG_SRC = ["'self'", "data:"]

CSP_BASE_URI = ["'none'"]
CSP_FRAME_ANCESTORS = ["'none'"]
CSP_FORM_ACTION = ["'self'", 'furconz.org.nz']

CSP_EXCLUDE_URL_PREFIXES = ('/admin',)

if not DEBUG:
    CSP_SCRIPT_SRC += ["'strict-dynamic'"]

# Database
# <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>
# <https://pypi.org/project/dj-database-url/>

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        cast=db_url
    )
}

CACHE_ENABLED = config('cache_enabled', default=False, cast=bool)

if CACHE_ENABLED:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': config('cache_location', default='127.0.0.1:11211'),
        }
    }

    # enable the cached session backend if caching is enabled
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        },
    }

# Authentication
# <https://django-allauth.readthedocs.io/en/latest/>

AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend'
]

ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.SignupForm',
    'login': 'apps.accounts.forms.LoginForm'
}

ACCOUNT_ADAPTER = 'apps.accounts.authentication.AccountAdapter'

ALLAUTH_2FA_ALWAYS_REVEAL_BACKUP_TOKENS = False

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

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

OIDC_SESSION_MANAGEMENT_ENABLE = True

# ReCAPTCHA
RECAPTCHA_DOMAIN = 'www.recaptcha.net'
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')

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
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(BASE_DIR, 'static_out')

if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = [
    ("bundles", os.path.join(BASE_DIR, 'assets/bundles'))
]

# noinspection PyUnresolvedReferences
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

SENTRY_ENABLED = config('sentry_enabled', default=False, cast=bool)

if SENTRY_ENABLED:
    SENTRY_DSN = config('sentry_dsn')

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    _vars = {
        'dsn': SENTRY_DSN,
        'send_default_pii': config('sentry_pii', default=False, cast=bool),
        'integrations': [DjangoIntegration()]
    }

    SENTRY_ENVIRONMENT = config('sentry_environment', default=False)

    if SENTRY_ENVIRONMENT:
        _vars['environment'] = SENTRY_ENVIRONMENT

    if config('sentry_git', default=False, cast=bool):
        import git

        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        _vars['release'] = sha

    sentry_sdk.init(**_vars)

# Email
# <https://sendgrid.com/docs/for-developers/sending-email/django/>
# <https://docs.djangoproject.com/en/2.2/topics/email/>

try:
    DEFAULT_FROM_EMAIL = config('email_from_user')
    SERVER_EMAIL = config('email_from_system')

    EMAIL_HOST = config('email_host', default='smtp.sendgrid.net')
    EMAIL_HOST_USER = config('email_user')
    EMAIL_HOST_PASSWORD = config('email_pass')
    EMAIL_PORT = config('email_port', default=587, cast=int)
    EMAIL_USE_TLS = config('email_tls', default=True, cast=bool)

except UndefinedValueError as e:
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

# MarkdownX
# <https://neutronx.github.io/django-markdownx/customization/>
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'pymdownx.smartsymbols',
    'pymdownx.betterem',
    'pymdownx.tilde',
    'pymdownx.caret',
    'pymdownx.emoji',
    'smarty'
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    'pymdownx.emoji': {
        'emoji_generator': pymdownx.emoji.to_alt
    }
}
