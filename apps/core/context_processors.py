from django.conf import settings


def site(request):
    response = {
        'DEBUG': settings.DEBUG
    }

    if settings.SENTRY_ENABLED:
        response['SENTRY_DSN'] = settings.SENTRY_DSN

    return response
