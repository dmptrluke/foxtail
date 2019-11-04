from django.conf import settings


def site(request):
    response = {
        'DEBUG': settings.DEBUG,
        'OIDC_SERVER': settings.OIDC_SERVER
    }

    if settings.SENTRY_ENABLED:
        response['SENTRY_DSN'] = settings.SENTRY_DSN

    return response
