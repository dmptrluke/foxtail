import logging

from django.conf import settings
from django.db import OperationalError, ProgrammingError

from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)


def site(request):
    return {
        'DEBUG': settings.DEBUG,
        'SITE_URL': settings.SITE_URL,
        'DEFAULT_COLOR_SCHEME': settings.DEFAULT_COLOR_SCHEME,
        'CDN_ORIGIN': settings.ASSET_HOSTS[0] if settings.ASSET_HOSTS else None,
        'UMAMI_SCRIPT_URL': settings.UMAMI_SCRIPT_URL,
        'UMAMI_WEBSITE_ID': settings.UMAMI_WEBSITE_ID,
    }


def conf(request):
    try:
        return {'conf': SiteSettings.get_solo()}
    except (OperationalError, ProgrammingError):
        logger.warning('SiteSettings table not available (pending migration?)')
        return {}


def debug(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = forwarded.split(',')[0] if forwarded else request.META.get('REMOTE_ADDR')
    return {
        'DEBUG_DATA_IP': ip,
        'DEBUG_DATA_VERSION': settings.BUILD_VERSION,
    }
