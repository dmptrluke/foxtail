from django.conf import settings
from django.utils.timezone import now


def site(request):
    return {'DEBUG': settings.DEBUG, 'DIRECTORY_ENABLED': settings.DIRECTORY_ENABLED, 'SITE_URL': settings.SITE_URL}


def debug(request):
    info = {}
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        info['ip'] = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else:
        info['ip'] = request.META.get('REMOTE_ADDR', None)
    if request.user.is_authenticated:
        info['user'] = request.user.username
    info['time'] = now().isoformat()

    return {'DEBUG_DATA': ' | '.join(f'{k}: {v}' for k, v in info.items())}
