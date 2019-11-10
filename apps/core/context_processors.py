from django.conf import settings


def site(request):
    response = {
        'DEBUG': settings.DEBUG,
        'SITE_URL': settings.SITE_URL
    }

    if settings.SENTRY_ENABLED:
        response['SENTRY_DSN'] = settings.SENTRY_DSN

    return response
