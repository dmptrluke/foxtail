import zoneinfo
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory
from django.utils import timezone

from ..middleware import RequestLoggingMiddleware, TimezoneMiddleware


class TestTimezoneMiddleware:
    def _make_middleware(self, response=None):
        return TimezoneMiddleware(lambda r: response or r)

    # activates a valid timezone from the session
    def test_activates_valid_timezone(self, request_factory: RequestFactory):
        mw = self._make_middleware()
        request = request_factory.get('/')
        request.session = {'django_timezone': 'Pacific/Auckland'}

        mw(request)

        assert str(timezone.get_current_timezone()) == 'Pacific/Auckland'

    # invalid timezone value is removed from the session
    def test_invalid_timezone_clears_session(self, request_factory: RequestFactory):
        mw = self._make_middleware()
        request = request_factory.get('/')
        request.session = {'django_timezone': 'Invalid/Zone'}

        mw(request)

        assert 'django_timezone' not in request.session

    # missing timezone deactivates to the project default
    def test_no_timezone_deactivates(self, request_factory: RequestFactory, settings):
        mw = self._make_middleware()
        request = request_factory.get('/')
        request.session = {}

        timezone.activate(zoneinfo.ZoneInfo('America/New_York'))

        mw(request)

        assert str(timezone.get_current_timezone()) == settings.TIME_ZONE


class TestRequestLoggingMiddleware:
    def _make_middleware(self):
        return RequestLoggingMiddleware(lambda r: HttpResponse('ok'))

    # regular request is logged with method, path, and status
    @patch('apps.core.middleware.logger')
    def test_logs_regular_request(self, mock_logger, request_factory: RequestFactory):
        mw = self._make_middleware()
        mw(request_factory.get('/some/path/'))

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[1] == 'GET'
        assert args[2] == '/some/path/'
        assert args[3] == 200

    # requests to /static/ are not logged
    @patch('apps.core.middleware.logger')
    def test_excludes_static_path(self, mock_logger, request_factory: RequestFactory):
        mw = self._make_middleware()
        mw(request_factory.get('/static/css/main.css'))

        mock_logger.info.assert_not_called()

    # requests to /health/ are not logged
    @patch('apps.core.middleware.logger')
    def test_excludes_health_path(self, mock_logger, request_factory: RequestFactory):
        mw = self._make_middleware()
        mw(request_factory.get('/health/'))

        mock_logger.info.assert_not_called()
