import logging
import zoneinfo
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('apps.core.access')

FURCONZ_REDIRECT_SESSION_KEY = 'show_furconz_welcome_banner'
FURCONZ_HOSTNAMES = {'furconz.org.nz', 'www.furconz.org.nz', 'furco.nz', 'www.furco.nz'}


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            try:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            except (ValueError, KeyError):
                del request.session['django_timezone']
        else:
            timezone.deactivate()
        return self.get_response(request)


class FurcoNZRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session = getattr(request, 'session', None)
        if session is not None:
            if self._is_furconz_referrer(request):
                session[FURCONZ_REDIRECT_SESSION_KEY] = True

            if settings.DEBUG and request.GET.get('from_furconz') == '1':
                session[FURCONZ_REDIRECT_SESSION_KEY] = True

        return self.get_response(request)

    def _is_furconz_referrer(self, request):
        referrer = request.headers.get('Referer', '')
        if not referrer:
            return False

        hostname = (urlparse(referrer).hostname or '').lower()
        return hostname in FURCONZ_HOSTNAMES


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.get_full_path()
        if not path.startswith(('/static/', '/health/')):
            logger.info(
                '"%s %s" %s %s',
                request.method,
                path,
                response.status_code,
                response.get('Content-Length', '-'),
            )
        return response
