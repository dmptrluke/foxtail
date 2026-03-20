"""
Django settings for Foxtail. Configured via environment variables and optional
.env file (django-environ).

Most settings should be configured via environment variables, not by editing
this file.

Sections: Core > Django > Third-party > Foxtail
Environment reference: deploy/foxtail/.env.example
"""

from pathlib import Path
from urllib.parse import urlparse

from django.contrib.messages import constants as messages

import environ
import pymdownx.emoji
from csp.constants import NONCE, NONE, SELF

SRC_DIR = Path(__file__).resolve(strict=True).parents[1]
BASE_DIR = SRC_DIR.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
SECRET_KEY_FALLBACKS = env.list('SECRET_KEY_FALLBACKS', default=[])

DEBUG = env.bool('DEBUG', default=False)  # debug toolbar, relaxed CSP, verbose messages, no conn pooling
TESTING = env.bool('TESTING', default=False)  # simplified staticfiles, silenced reCAPTCHA check

SITE_URL = env('SITE_URL').rstrip('/')
SITE_DOMAIN = urlparse(SITE_URL).hostname
DEFAULT_COLOR_SCHEME = env('DEFAULT_COLOR_SCHEME', default='plum')
if DEFAULT_COLOR_SCHEME not in {'plum', 'coffee', 'autumn', 'forest', 'slate'}:
    raise ValueError(f'DEFAULT_COLOR_SCHEME must be one of the valid color schemes, got {DEFAULT_COLOR_SCHEME!r}')

ROOT_URLCONF = 'foxtail.urls'

WSGI_APPLICATION = 'foxtail.wsgi.application'

INSTALLED_APPS = [
    'apps.admin.apps.CustomAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_vite',
    'django.forms',
    'django_cotton',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django.contrib.sitemaps',
    'rules.apps.AutodiscoverRulesConfig',
    'markdownfield',
    'cjswidget',
    'published',
    'structured_data',
    'solo',
    'csp',
    'csp_helpers',
    'formguard',
    'apps.core',
    'apps.email',
    'apps.accounts',
    'apps.content',
    'apps.events',
    'apps.organisations',
    'apps.blog',
    'apps.contact',
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.openid_connect',
    'anymail',
    'taggit',
    'widget_tweaks',
    'allauth.idp',
    'allauth.idp.oidc',
    'django_recaptcha',
    'imagefield',
    'huey.contrib.djhuey',
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
    'apps.core.middleware.FetchMetadataMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG,
    }

# =============================================================================
# Django
# =============================================================================

# Hosting
# <https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts>

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[]) + ['localhost']
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Caddy handles HSTS and HTTP->HTTPS redirect at the reverse proxy layer
SILENCED_SYSTEM_CHECKS = ['security.W004', 'security.W008']

# Template Engine
# <https://docs.djangoproject.com/en/stable/topics/templates/>

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(SRC_DIR / 'templates').as_posix()],
        'OPTIONS': {
            'loaders': [
                (
                    'django.template.loaders.cached.Loader',
                    [
                        'django_cotton.cotton_loader.Loader',
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ],
                ),
            ],
            'builtins': [
                'django_cotton.templatetags.cotton',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site',
                'apps.core.context_processors.conf',
                'apps.core.context_processors.debug',
                'csp.context_processors.nonce',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'
FORMS_URLFIELD_ASSUME_HTTPS = True

# Database
# <https://docs.djangoproject.com/en/stable/ref/settings/#databases>

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {'default': env.db('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))}
DATABASES['default']['CONN_MAX_AGE'] = 0 if DEBUG else env.int('CONN_MAX_AGE', default=600)
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Cache
# <https://docs.djangoproject.com/en/stable/topics/cache/#setting-up-the-cache>

CACHES = {
    'default': env.cache(default='dummycache://'),
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

# Sessions
# <https://docs.djangoproject.com/en/stable/topics/http/sessions/#using-cached-sessions>

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 2592000  # 30 days

# Authentication
# <https://docs.djangoproject.com/en/stable/topics/auth/>

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'

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

# Internationalization
# <https://docs.djangoproject.com/en/stable/topics/i18n/>

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Auckland'
USE_I18N = True
USE_TZ = True

# Messages
# <https://docs.djangoproject.com/en/stable/ref/contrib/messages/>

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
# <https://docs.djangoproject.com/en/stable/ref/settings/#media-root>

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = [str(BASE_DIR / 'build/static'), str(BASE_DIR / 'assets/static')]


S3_MEDIA = env.bool('S3_MEDIA', default=False)

if S3_MEDIA:
    AWS_ACCESS_KEY_ID = env('S3_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = env('S3_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = env('S3_BUCKET')
    AWS_S3_ENDPOINT_URL = env('S3_ENDPOINT')
    AWS_S3_CUSTOM_DOMAIN = env('S3_DOMAIN', default=None)
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False

STORAGES = {
    'default': {
        'BACKEND': 'apps.core.storages.MediaS3Storage' if S3_MEDIA else 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
STATIC_ROOT = str(BASE_DIR / 'static')
WHITENOISE_MAX_AGE = 31536000

if not S3_MEDIA:
    MEDIA_ROOT = str(BASE_DIR / 'storage/media')

if TESTING:
    WHITENOISE_AUTOREFRESH = True
    STORAGES['staticfiles'] = {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    }

# django-vite
# <https://github.com/MrBin99/django-vite>

VITE_DEV_MODE = env.bool('VITE_DEV_MODE', default=False)

DJANGO_VITE = {
    'default': {
        'dev_mode': VITE_DEV_MODE,
        'dev_server_host': 'localhost',
        'dev_server_port': 5173,
        'manifest_path': str(BASE_DIR / 'build' / 'static' / '.vite' / 'manifest.json'),
    },
}

# Security
# <https://docs.djangoproject.com/en/stable/howto/deployment/checklist/#https>

CSRF_TRUSTED_ORIGINS = [SITE_URL]
CSRF_COOKIE_NAME = '__Host-csrftoken'
CSRF_COOKIE_SECURE = True
CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'

SESSION_COOKIE_NAME = '__Host-sessionid'
SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

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

# Logging
# <https://docs.djangoproject.com/en/stable/ref/settings/#logging>
# <https://docs.djangoproject.com/en/stable/topics/logging>

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
        'botocore': {'level': 'WARNING'},
        's3transfer': {'level': 'WARNING'},
        'pyvips': {'level': 'WARNING'},
        'django.request': {'level': 'ERROR', 'handlers': ['console'], 'propagate': False},
        'apps.core.access': {
            'level': 'INFO',
            'handlers': ['access'],
            'propagate': False,
        },
    },
}

if DEBUG:
    _log_file = str(BASE_DIR / 'logs' / 'django.log')
    LOGGING['handlers']['file'] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': _log_file,
        'formatter': 'verbose',
    }
    LOGGING['handlers']['access_file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': _log_file,
        'formatter': 'access',
    }
    LOGGING['root']['handlers'].append('file')
    LOGGING['loggers']['apps.core.access']['handlers'].append('access_file')

# =============================================================================
# Third-party
# =============================================================================

# allauth
# <https://docs.allauth.org/en/latest/account/configuration.html>

ACCOUNT_ADAPTER = 'apps.accounts.authentication.AccountAdapter'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_SESSION_REMEMBER = True

ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_LOGIN_BY_CODE_ENABLED = False

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
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
    'verify_generate': '5/m/user',
    'verify_submit': '10/m/ip',
    'verify_unverify': '5/m/user',
}

# allauth social
# <https://docs.allauth.org/en/latest/socialaccount/configuration.html>

SOCIALACCOUNT_ADAPTER = 'apps.accounts.authentication.SocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False

SOCIALACCOUNT_PROVIDERS = {}

_github_client_id = env('GITHUB_CLIENT_ID', default='')
if _github_client_id:
    SOCIALACCOUNT_PROVIDERS['github'] = {
        'SCOPE': ['read:user', 'user:email'],
        'APPS': [{'client_id': _github_client_id, 'secret': env('GITHUB_CLIENT_SECRET')}],
    }

_google_client_id = env('GOOGLE_CLIENT_ID', default='')
if _google_client_id:
    SOCIALACCOUNT_PROVIDERS['google'] = {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APPS': [{'client_id': _google_client_id, 'secret': env('GOOGLE_CLIENT_SECRET')}],
    }

_discord_client_id = env('DISCORD_CLIENT_ID', default='')
if _discord_client_id:
    SOCIALACCOUNT_PROVIDERS['discord'] = {
        'APPS': [{'client_id': _discord_client_id, 'secret': env('DISCORD_CLIENT_SECRET')}],
    }

_telegram_client_id = env('TELEGRAM_CLIENT_ID', default='')
if _telegram_client_id:
    SOCIALACCOUNT_PROVIDERS['openid_connect'] = {
        'OAUTH_PKCE_ENABLED': True,
        'APPS': [
            {
                'provider_id': 'telegram',
                'name': 'Telegram',
                'client_id': _telegram_client_id,
                'secret': env('TELEGRAM_CLIENT_SECRET'),
                'settings': {
                    'server_url': 'https://oauth.telegram.org',
                    'scope': ['openid', 'profile'],
                    'fetch_userinfo': False,
                },
            },
        ],
    }

# allauth-mfa
# <https://docs.allauth.org/en/latest/mfa/index.html>

MFA_SUPPORTED_TYPES = ['recovery_codes', 'totp', 'webauthn']
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

# allauth idp
# <https://docs.allauth.org/en/latest/idp/oidc/index.html>

IDP_OIDC_ADAPTER = 'apps.accounts.adapter.FoxtailOIDCAdapter'
IDP_OIDC_PRIVATE_KEY = env('OIDC_RSA_PRIVATE_KEY', default='')

# CSP Headers
# <https://django-csp.readthedocs.io/en/latest/>

ASSET_HOSTS = env.list('ASSET_HOSTS', default=[])

_csp_script_src = [
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
        'style-src': [SELF, NONCE] + ASSET_HOSTS,
        'style-src-attr': ["'unsafe-inline'"],
        'frame-src': [
            'https://www.google.com/recaptcha/',
            'https://www.youtube.com',
            'https://www.youtube-nocookie.com',
        ],
        'font-src': [SELF] + ASSET_HOSTS,
        'img-src': [SELF, 'data:', 'https://api.maptiler.com'] + ASSET_HOSTS,
        'object-src': [NONE],
        'worker-src': ['blob:'],
        'connect-src': [SELF, 'https://sentry.io', 'https://api.maptiler.com', 'https://www.google.com/recaptcha/'],
        'base-uri': [NONE],
        'frame-ancestors': [NONE],
        # form-action removed: Chrome blocks reCAPTCHA invisible widget form.submit()
        # calls as cross-origin (iframe callback context). script-src nonce policy
        # prevents form injection attacks. CSP_FORM_ACTION env var also retired.
        'upgrade-insecure-requests': not DEBUG,
        'report-uri': env('CSP_REPORT_URI', default=None),
    },
}

if VITE_DEV_MODE:
    CONTENT_SECURITY_POLICY['DIRECTIVES']['script-src'] += ['http://localhost:5173']
    CONTENT_SECURITY_POLICY['DIRECTIVES']['connect-src'] += ['ws://localhost:5173']
    CONTENT_SECURITY_POLICY['DIRECTIVES']['font-src'] += ['http://localhost:5173']
    CONTENT_SECURITY_POLICY['DIRECTIVES']['img-src'] += ['http://localhost:5173']

if DEBUG:
    CONTENT_SECURITY_POLICY['DIRECTIVES']['style-src'] = ["'unsafe-inline'", SELF] + ASSET_HOSTS

# django-imagefield
# <https://django-imagefield.readthedocs.io/en/latest/>

MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

IMAGEFIELD_BACKEND = 'vips'
IMAGEFIELD_AUTOGENERATE = False
IMAGEFIELD_BIN_DEPTH = 2
IMAGEFIELD_FORMATS = {
    'accounts.user.avatar': {
        'small': ['default', ('crop', (80, 80))],
        'medium': ['default', ('crop', (160, 160))],
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
        'card': ['default', ('crop', (600, 315))],
        'card_2x': ['default', ('crop', (1200, 630))],
        'banner': ['default', ('crop', (1440, 443))],
        'banner_2x': ['default', ('crop', (2880, 886))],
        'tall': ['default', ('crop', (960, 768))],
        'tall_2x': ['default', ('crop', (1920, 1536))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'events.event.image': {
        'card': ['default', ('crop', (600, 315))],
        'card_2x': ['default', ('crop', (1200, 630))],
        'banner': ['default', ('crop', (1440, 443))],
        'banner_2x': ['default', ('crop', (2880, 886))],
        'tall': ['default', ('crop', (960, 768))],
        'tall_2x': ['default', ('crop', (1920, 1536))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'organisations.organisation.logo': {
        'square': ['default', ('crop', (400, 400))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
    'organisations.eventseries.logo': {
        'square': ['default', ('crop', (400, 400))],
        'admin': ['default', ('thumbnail', (300, 300))],
    },
}

# huey
# <https://huey.readthedocs.io/en/latest/django.html>

HUEY = {
    'huey_class': 'huey.RedisHuey',
    'name': 'foxtail',
    'immediate': env.bool('HUEY_IMMEDIATE', default=False),
    'results': False,
    'url': env.str('CACHE_URL', default='redis://redis/1'),
    'consumer': {
        'workers': 1,
        'worker_type': 'thread',
    },
}

# Markdown
# <https://github.com/jamesturk/django-markdownfield>

MARKDOWN_EXTENSIONS = [
    'pymdownx.smartsymbols',
    'pymdownx.betterem',
    'pymdownx.tilde',
    'pymdownx.caret',
    'pymdownx.emoji',
    'pymdownx.magiclink',
    'sane_lists',
    'def_list',
    'nl2br',
    'abbr',
    'smarty',
]

MARKDOWN_EXTENSION_CONFIGS = {'pymdownx.emoji': {'emoji_generator': pymdownx.emoji.to_alt}}

MARKDOWN_LINK_BLACKLIST = ['furry.nz', 'furry.org.nz']

# ReCAPTCHA
# <https://pypi.org/project/django-recaptcha/>

TEST_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
TEST_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

if DEBUG or TESTING:
    SILENCED_SYSTEM_CHECKS += ['django_recaptcha.recaptcha_test_key_error']

FORMGUARD_SUCCESS_MESSAGE = 'Your message has been sent.'

RECAPTCHA_INVISIBLE = env.bool('RECAPTCHA_INVISIBLE', default=True)
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default=TEST_PUBLIC_KEY)
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default=TEST_PRIVATE_KEY)

# Build metadata

GIT_SHA = env('GIT_SHA', default='')
RELEASE_VERSION = env('RELEASE_VERSION', default='')
BUILD_VERSION = RELEASE_VERSION or (GIT_SHA[:8] if GIT_SHA else '')

# Sentry.io
# <https://docs.sentry.io/platforms/python/django/>

SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    _vars = {
        'dsn': SENTRY_DSN,
        'send_default_pii': env.bool('SENTRY_PII', default=False),
        'integrations': [DjangoIntegration(cache_spans=True), RedisIntegration()],
        'traces_sample_rate': env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.2),
        'profiles_sample_rate': env.float('SENTRY_PROFILES_SAMPLE_RATE', default=0.2),
    }

    SENTRY_ENVIRONMENT = env('SENTRY_ENVIRONMENT', default='')
    if SENTRY_ENVIRONMENT:
        _vars['environment'] = SENTRY_ENVIRONMENT

    if RELEASE_VERSION or GIT_SHA:
        _vars['release'] = RELEASE_VERSION or GIT_SHA

    if env.bool('SENTRY_CSP', default=False):
        from urllib.parse import urlparse

        _csp_report_uri = 'https://sentry.io/api/{}/security/?sentry_key={}'.format(
            urlparse(SENTRY_DSN).path.strip('/'), urlparse(SENTRY_DSN).username
        )
        if _vars.get('release'):
            _csp_report_uri += f'&sentry_release={_vars["release"]}'
        CONTENT_SECURITY_POLICY['DIRECTIVES']['report-uri'] = _csp_report_uri

    sentry_sdk.init(**_vars)

# Taggit
# <https://django-taggit.readthedocs.io/en/latest/getting_started.html>

TAGGIT_CASE_INSENSITIVE = True

# django-solo
# <https://github.com/lazybird/django-solo>

SOLO_CACHE = 'locmem'
SOLO_CACHE_TIMEOUT = 60 * 5

# django-structured-data
# <https://github.com/dmptrluke/django-structured-data>


def _sitewide_structured_data():
    from apps.core.models import SiteSettings

    s = SiteSettings.get_solo()
    return [
        {
            '@type': 'Organization',
            '@id': f'{SITE_URL}/#organization',
            'name': s.org_name,
            'url': SITE_URL,
            'logo': {
                '@type': 'ImageObject',
                'url': 'https://cdn.furry.nz/static/images/paw-dark@3x.png',
                'width': 90,
                'height': 90,
            },
        },
    ]


def _sitewide_og_data():
    from apps.core.models import SiteSettings

    s = SiteSettings.get_solo()
    return {
        'og:site_name': s.org_name,
        'og:locale': 'en_NZ',
        'og:logo': 'https://cdn.furry.nz/static/images/paw-dark@3x.png',
    }


STRUCTURED_DATA_SITEWIDE = _sitewide_structured_data
STRUCTURED_DATA_SITEWIDE_OG = _sitewide_og_data

# =============================================================================
# Foxtail
# =============================================================================

CONTACT_EMAILS = env.list('CONTACT_EMAILS')

MAPTILER_API_KEY = env('MAPTILER_API_KEY', default='')
ROBOTS_ALLOWED = env.bool('ROBOTS_ALLOWED', default=True)
