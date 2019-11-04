from django.shortcuts import render
from sentry_sdk import last_event_id


def handler_400(request, *args, **kwargs):
    return render(request, 'error_pages/400.html', status=400)


def handler_403(request, *args, **kwargs):
    return render(request, 'error_pages/403.html', status=403)


def handler_404(request, *args, **kwargs):
    return render(request, 'error_pages/404.html', status=404)


def handler_500(request, *args, **kwargs):
    context = {'sentry_event_id': last_event_id()}
    return render(request, 'error_pages/500.html', context=context, status=500)
