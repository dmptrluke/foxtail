import json
import logging
from functools import cached_property
from textwrap import dedent

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views import View
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def health(request):
    return HttpResponse('ok')


@require_GET
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

    return HttpResponse(text, content_type='text/plain')


IN_APP_BROWSERS = [
    ('TelegramAndroid', 'Telegram'),
    ('TelegramiOS', 'Telegram'),
    ('FBAN', 'Facebook'),
    ('FBAV', 'Facebook'),
    ('Instagram', 'Instagram'),
    ('Line/', 'LINE'),
    ('MicroMessenger', 'WeChat'),
    ('Twitter', 'X (Twitter)'),
    ('Snapchat', 'Snapchat'),
    ('Discord', 'Discord'),
]


def csrf_failure(request, reason=''):
    ua = request.META.get('HTTP_USER_AGENT', '')
    app_name = ''
    for signature, name in IN_APP_BROWSERS:
        if signature in ua:
            app_name = name
            break
    return render(
        request,
        '403_csrf.html',
        {'in_app_browser': app_name},
        status=403,
    )


def handler_500(request, *args, **kwargs):
    try:
        return render(request, '500.html', status=500)
    except Exception:
        logger.exception('Dynamic 500 template failed, using static fallback')
        html = loader.get_template('500_static.html').render()
        return HttpResponse(html, status=500, content_type='text/html')


@require_GET
def test_error(request, code):
    """Debug-only view for previewing error pages."""
    templates = {
        400: ('400.html', {}),
        403: ('403.html', {}),
        404: ('404.html', {}),
        500: ('500.html', {}),
    }
    template, context = templates.get(code, ('404.html', {}))
    return render(request, template, context=context, status=code)


class ApiView(View):
    """Base for JSON endpoints. Handles auth, error formatting, and body parsing."""

    require_auth = True

    def dispatch(self, request, *args, **kwargs):
        if self.require_auth and not request.user.is_authenticated:
            return self.error('Authentication required', 403)
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return self.error('Not found', 404)
        except PermissionDenied:
            return self.error('Forbidden', 403)
        except Exception:
            # API boundary: always return JSON, never leak tracebacks to clients
            logger.exception('Unhandled error in %s', self.__class__.__name__)
            return self.error('Internal server error', 500)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return self.error('Method not allowed', 405)

    @cached_property
    def data(self):
        if self.request.content_type == 'application/json':
            try:
                return json.loads(self.request.body)
            except (json.JSONDecodeError, ValueError):
                return {}
        return self.request.POST

    def success(self, data=None, status=200):
        return JsonResponse(data or {}, status=status)

    def error(self, message, status=400):
        return JsonResponse({'error': message}, status=status)
