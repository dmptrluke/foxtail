import json

from django.conf import settings
from django.utils.timezone import now


def site(request):
    response = {
        'DEBUG': settings.DEBUG,
        'DIRECTORY_ENABLED': settings.DIRECTORY_ENABLED,
        'SITE_URL': settings.SITE_URL
    }

    if settings.SENTRY_ENABLED:
        response['SENTRY_DSN'] = settings.SENTRY_DSN

    return response


def debug(request):
    info = {}
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        info['ip'] = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else:
        info['ip'] = request.META.get('REMOTE_ADDR', None)
    if request.user.is_authenticated:
        info['user'] = request.user.username
    info['time'] = now().isoformat()

    return {
        'DEBUG_DATA': json.dumps(info)
    }
