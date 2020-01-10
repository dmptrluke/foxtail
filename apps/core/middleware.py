from django.utils import timezone

import pytz


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except (ValueError, pytz.UnknownTimeZoneError):
                del request.session['django_timezone']
        else:
            timezone.deactivate()
        return self.get_response(request)
