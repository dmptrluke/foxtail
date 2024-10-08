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
from pathlib import Path

from django.contrib.messages import constants as messages

import environ
import pymdownx.emoji

logger = logging.getLogger(__name__)

# Build paths inside the project like this: str(BASE_DIR / 'subdir').
BASE_DIR = Path(__file__).resolve(strict=True).parents[1]

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
INTERNAL_IPS = env.list('INTERNAL_IPS', default=[])
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
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django.contrib.sitemaps',
    'rules.apps.AutodiscoverRulesConfig',
    'markdownfield',
    'cjswidget',
    'published',
    'structured_data',
    'csp_helpers',
    'apps.core',
    'apps.email',
    'apps.accounts',
    'apps.content',
    'apps.events',
    'apps.directory',
    'foxtail_blog',
    'foxtail_contact',
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.github',
    'anymail',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'mail_templated_simple',
    'taggit',
    'webpack_loader',
    'crispy_forms',
    'crispy_bootstrap5',
    'oidc_provider',
    'django_recaptcha',
    'versatileimagefield',
    'django_rq',
    'django_cleanup.apps.CleanupConfig',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'nplusone.ext.django',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
]

if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'nplusone.ext.django.NPlusOneMiddleware',
    ]

# Template Engine
# <https://docs.djangoproject.com/en/dev/topics/templates/>

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(BASE_DIR / 'templates').as_posix()],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'apps.core.context_processors.site',
                'apps.core.context_processors.debug',
                'csp.context_processors.nonce'
            ],
        },
    },
]

# Recognise upstream proxy SSL
# <https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header>
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
# <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')
    )
}

# Cache
# <https://docs.djangoproject.com/en/2.2/topics/cache/#setting-up-the-cache>
CACHES = {
    'default': env.cache(default='dummycache://')
}

# enable the cached session backend
# <https://docs.djangoproject.com/en/2.2/topics/http/sessions/#using-cached-sessions>
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# django-rq
# <https://github.com/rq/django-rq>
RQ_ASYNC = env.bool('RQ_ASYNC', default=True)

RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'ASYNC': RQ_ASYNC
    }
}

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

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

ACCOUNT_USERNAME_VALIDATORS = 'apps.accounts.validators.username_validators'

ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.SignupForm',
    'change_password': 'apps.accounts.forms.ChangePasswordForm',
    'set_password': 'apps.accounts.forms.SetPasswordForm',
    'reset_password': 'apps.accounts.forms.ResetPasswordForm',
    'login': 'apps.accounts.forms.LoginForm'
}

# allauth social
SOCIALACCOUNT_ADAPTER = 'apps.accounts.authentication.SocialAccountAdapter'
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

# allauth-mfa

MFA_FORMS = {
    'authenticate': 'allauth.mfa.base.forms.AuthenticateForm',
    'reauthenticate': 'allauth.mfa.base.forms.AuthenticateForm',
    'activate_totp': 'allauth.mfa.totp.forms.ActivateTOTPForm',
    'deactivate_totp': 'allauth.mfa.totp.forms.DeactivateTOTPForm',
    'generate_recovery_codes': 'allauth.mfa.recovery_codes.forms.GenerateRecoveryCodesForm',
}

# OpenID Connect Provider
# <https://django-oidc-provider.readthedocs.io/en/latest/>
OIDC_SESSION_MANAGEMENT_ENABLE = True
OIDC_SESSION_MANAGEMENT_COOKIE_SECURE = True
OIDC_USERINFO = 'apps.accounts.claims.userinfo'

OIDC_CLAIMS_SUPPORTED = [
    'sub',
    'name',
    'preferred_username',
    'nickname',
    'birthdate',
    'email',
    'email_verified'
]

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

# ReCAPTCHA
# <https://pypi.org/project/django-recaptcha/>

# I used to pull these from captcha.constants, but it does some annoying stuff
# and seems to run all of the Django system checks if I even touch that module
TEST_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
TEST_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

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
# <https://docs.djangoproject.com/en/2.2/topics/i18n/>

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Auckland'

USE_I18N = True
USE_L10N = True
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
# <https://docs.djangoproject.com/en/2.2/howto/static-files/>
# <https://docs.djangoproject.com/en/dev/ref/settings/#media-root>

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = [
    ("webpack_bundles", str(BASE_DIR / 'assets/generated/webpack_bundles')),
    str(BASE_DIR / 'assets/static')
]

AZURE_STATIC = env.bool('AZURE_STATIC', default=False)
AZURE_MEDIA = env.bool('AZURE_MEDIA', default=False)

if AZURE_STATIC or AZURE_MEDIA:
    AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT')
    AZURE_ACCOUNT_KEY = env('AZURE_KEY')
    AZURE_CUSTOM_DOMAIN = env('AZURE_DOMAIN', default=None)

    AZURE_SSL = env.bool('AZURE_SSL', default=True)
    AZURE_EMULATED_MODE = env.bool('AZURE_EMULATED', default=False)


if AZURE_STATIC:
    STATICFILES_STORAGE = 'apps.core.storages.StaticAzureStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    STATIC_ROOT = str(BASE_DIR / 'static')

if AZURE_MEDIA:
    DEFAULT_FILE_STORAGE = 'apps.core.storages.MediaAzureStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = str(BASE_DIR / 'storage/media')

if TESTING:
    WHITENOISE_AUTOREFRESH = True

# Webpack Loader
# <https://github.com/owais/django-webpack-loader>
WEBPACK_STATS_PATH = env('WEBPACK_STATS_PATH', default='assets/generated/webpack-stats.json')

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, WEBPACK_STATS_PATH),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Security
# <https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/#https>
# <https://docs.djangoproject.com/en/2.2/ref/middleware/#x-xss-protection>

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = '__Host-sessionid'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = '__Host-csrftoken'

SECURE_BROWSER_XSS_FILTER = True

# this header is applied with nginx
SECURE_CONTENT_TYPE_NOSNIFF = False

X_FRAME_OPTIONS = 'DENY'

# CSP Headers
# <https://django-csp.readthedocs.io/en/latest/>

CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
CSP_UPGRADE_INSECURE_REQUESTS = True

ASSET_HOSTS = env.list('ASSET_HOSTS', default=[])

CSP_DEFAULT_SRC = ["'self'"]

CSP_REPORT_URI = env('CSP_REPORT_URI', default=None)

CSP_SCRIPT_SRC = ["'unsafe-inline'", "'self'", 'https://www.google.com/recaptcha/',
                  'https://www.gstatic.com/recaptcha/'] + ASSET_HOSTS
CSP_STYLE_SRC = ["'unsafe-inline'", 'fonts.googleapis.com', "'self'"] + ASSET_HOSTS
CSP_FRAME_SRC = ['https://www.google.com/recaptcha/']
CSP_FONT_SRC = ["'self'", 'data:', 'fonts.gstatic.com'] + ASSET_HOSTS
CSP_IMG_SRC = ["'self'", 'data:', 'ui-avatars.com', '*.wp.com', 'www.gravatar.com'] + ASSET_HOSTS
CSP_OBJECT_SRC = ["'none'"]
CSP_CONNECT_SRC = ["'self'", 'https://sentry.io']

CSP_BASE_URI = ["'none'"]
CSP_FRAME_ANCESTORS = ["'none'"]
# CSP_FORM_ACTION = ["'self'"] + env.list('CSP_FORM_ACTION', default=[])

CSP_EXCLUDE_URL_PREFIXES = ('/admin',)

# we don't use strict-dynamic in debug because it breaks django-debug-toolbar
if not DEBUG:
    CSP_SCRIPT_SRC += ["'strict-dynamic'"]

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
        'integrations': [DjangoIntegration(), RedisIntegration()]
    }

    # attach environment
    SENTRY_ENVIRONMENT = env('sentry_environment', default=False)
    if SENTRY_ENVIRONMENT:
        _vars['environment'] = SENTRY_ENVIRONMENT

    # attach version
    if env.bool('SENTRY_GIT', default=False):
        import git
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        _vars['release'] = sha
        repo.close()

    # set CSP report URI
    if env('SENTRY_CSP', default=False):
        CSP_REPORT_URI = "https://sentry.io/api/{}/security/?sentry_key={}".format(
            urlparse(SENTRY_DSN).path.strip('/'),
            urlparse(SENTRY_DSN).username
        )

        if _vars.get('release'):
            CSP_REPORT_URI += f"&sentry_release={_vars['release']}"

    sentry_sdk.init(**_vars)

# Logging
# <https://docs.djangoproject.com/en/dev/ref/settings/#logging>
# <https://docs.djangoproject.com/en/dev/topics/logging>
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] [%(process)d] [%(levelname)s] (%(module)s) %(message)s"
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
        "nplusone": {
            "level": "WARN",
            "handlers": ["console"]
        },
        "sentry_sdk": {
            "level": "ERROR",
            "handlers": ["console"]
        },
    },
}

# Email
# <https://docs.djangoproject.com/en/2.2/topics/email/>
# <https://anymail.readthedocs.io/en/stable/>
DEFAULT_FROM_EMAIL = env('EMAIL_FROM_USER', default='webmaster@localhost')
SERVER_EMAIL = env('EMAIL_FROM_SYSTEM', default='root@localhost')

if 'MAILGUN_API_KEY' in env:
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL_MAILGUN_API_KEY = env('MAILGUN_API_KEY')

    if 'MAILGUN_SENDER_DOMAIN' in env:
        ANYMAIL_MAILGUN_SENDER_DOMAIN = env('MAILGUN_SENDER_DOMAIN')

else:
    EMAIL_CONFIG = env.email_url('EMAIL_URL', default='consolemail://')
    vars().update(EMAIL_CONFIG)

EMAIL_REAL_BACKEND = EMAIL_BACKEND
EMAIL_BACKEND = 'apps.email.engine.AsyncEmailBackend'

# Crispy Forms
# <https://django-crispy-forms.readthedocs.io/en/latest/>
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# VersatileImageField
# <https://django-versatileimagefield.readthedocs.io/en/latest/installation.html#versatileimagefield-settings>
VERSATILEIMAGEFIELD_SETTINGS = {
    'jpeg_resize_quality': 80,
    'cache_name': 'vif',
    'create_images_on_demand': False,
    'sized_directory_name': '_s',
    'filtered_directory_name': '_f'
}

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    'event_image': [
        ('mini', 'crop__350x175'),
        ('mini2x', 'crop__700x350'),
        ('banner', 'crop__1150x300'),
        ('admin', 'thumbnail__300x300')
    ],
    'post_image': [
        ('mini', 'crop__350x175'),
        ('mini2x', 'crop__700x350'),
        ('banner', 'crop__800x350'),
        ('banner2x', 'crop__1200x525'),
        ('admin', 'thumbnail__300x300')
    ]
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

MARKDOWN_LINKIFY_BLACKLIST = env.list('MARKDOWN_LINKIFY_BLACKLIST', default=[])

# robots.txt
ROBOTS_ALLOWED = env.bool('ROBOTS_ALLOWED', default=True)

# Django Structured Data
# <https://github.com/dmptrluke/django-structured-data>
DEFAULT_STRUCTURED_DATA = {
    "publisher": {
        "@id": "https://furry.nz/#organization",
    }
}


# Foxtail Blog
# <https://github.com/dmptrluke/foxtail-blog>

BLOG_COMMENTS = True
BLOG_FEED_TITLE = "Latest News"
BLOG_FEED_DESCRIPTION = "The latest furry news."

# Foxtail Contact
# <https://github.com/dmptrluke/foxtail-contact>

CONTACT_EMAILS = env.list('CONTACT_EMAILS')

# Foxtail
DIRECTORY_ENABLED = env.bool('DIRECTORY_ENABLED', default=False)
