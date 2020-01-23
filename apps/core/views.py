from textwrap import dedent

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render


def robots(request):
    if settings.ROBOTS_ALLOWED:
        text = dedent(f"""\
            User-agent: *
            Disallow:

            Sitemap: {settings.SITE_URL}/sitemap.xml
        """)
    else:
        text = dedent("""\
            User-agent: *
            Disallow: /
            """)

    return HttpResponse(text, content_type="text/plain")


def handler_500(request, *args, **kwargs):
    if settings.SENTRY_ENABLED:
        from sentry_sdk import last_event_id

        context = {'sentry_event_id': last_event_id()}
    else:
        context = {}

    return render(request, '500.html', context=context, status=500)


def redirect_provider_info(request, *args, **kwargs):
    return redirect('oidc_provider:provider-info')
