from django.conf import settings


def site(request):
    return {'DEBUG': settings.DEBUG, 'SITE_URL': settings.SITE_URL}


def debug(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = forwarded.split(',')[0] if forwarded else request.META.get('REMOTE_ADDR')
    return {'DEBUG_DATA_IP': ip}
