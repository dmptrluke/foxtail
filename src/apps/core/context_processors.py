from django.conf import settings


def site(request):
    return {
        'DEBUG': settings.DEBUG,
        'SITE_URL': settings.SITE_URL,
        'DEFAULT_COLOR_SCHEME': settings.DEFAULT_COLOR_SCHEME,
    }


def debug(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = forwarded.split(',')[0] if forwarded else request.META.get('REMOTE_ADDR')
    release = settings.GIT_SHA
    return {
        'DEBUG_DATA_IP': ip,
        'DEBUG_DATA_VERSION': release[:8] if release else '',
    }
