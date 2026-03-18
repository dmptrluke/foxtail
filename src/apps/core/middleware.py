import logging
import zoneinfo

from django.http import HttpResponseForbidden
from django.utils import timezone

logger = logging.getLogger('apps.core.access')

SAFE_METHODS = frozenset(('GET', 'HEAD', 'OPTIONS', 'TRACE'))
ALLOWED_FETCH_SITES = frozenset(('same-origin', 'none'))


class FetchMetadataMiddleware:
    """Reject cross-site state-changing requests using Sec-Fetch-Site."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in SAFE_METHODS:
            fetch_site = request.META.get('HTTP_SEC_FETCH_SITE')
            if fetch_site and fetch_site not in ALLOWED_FETCH_SITES:
                return HttpResponseForbidden('Cross-site request blocked.')
        return self.get_response(request)


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
