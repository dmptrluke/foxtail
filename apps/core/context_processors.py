from django.conf import settings


def site(request):
    return {
        'DEBUG': settings.DEBUG,
        'OIDC_SERVER': settings.OIDC_SERVER
    }
