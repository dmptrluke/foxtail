from django.conf import settings
from django.shortcuts import render


def handler_400(request, *args, **kwargs):
    return render(request, 'error_pages/400.html', status=400)


def handler_403(request, *args, **kwargs):
    return render(request, 'error_pages/403.html', status=403)


def handler_404(request, *args, **kwargs):
    return render(request, 'error_pages/404.html', status=404)


def handler_500(request, *args, **kwargs):
    if settings.SENTRY_ENABLED:
        from sentry_sdk import last_event_id

        context = {'sentry_event_id': last_event_id()}
    else:
        context = {}

    return render(request, 'error_pages/500.html', context=context, status=500)
