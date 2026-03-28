import logging
import zoneinfo

from django.utils import timezone

logger = logging.getLogger('apps.core.access')


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
