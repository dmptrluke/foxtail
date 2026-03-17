from textwrap import dedent
from unittest.mock import patch

from django.test import RequestFactory

import pytest

from ..views import csrf_failure, handler_500, robots

pytestmark = pytest.mark.django_db


class TestRobotsView:
    # robots.txt permits crawling and includes sitemap URL when allowed
    def test_allowed(self, request_factory: RequestFactory, settings):
        settings.ROBOTS_ALLOWED = True
        response = robots(request_factory.get('/robots.txt'))

        assert response['content-type'] == 'text/plain'
        assert response.content.decode() == dedent(f"""\
            User-agent: *
            Disallow:

            Sitemap: {settings.SITE_URL}/sitemap.xml
        """)

    # robots.txt blocks all crawling when disallowed
    def test_disallowed(self, request_factory: RequestFactory, settings):
        settings.ROBOTS_ALLOWED = False
        response = robots(request_factory.get('/robots.txt'))

        assert response['content-type'] == 'text/plain'
        assert response.content.decode() == dedent("""\
            User-agent: *
            Disallow: /
        """)


class TestHealthView:
    # health endpoint returns 200 with plain text body
    def test_returns_ok(self, client):
        response = client.get('/health/')
        assert response.status_code == 200
        assert response.content == b'ok'


class TestHandler500:
    # 500 handler renders with empty context when Sentry is not configured
    @patch('apps.core.views.render')
    def test_without_sentry(self, mock_render, request_factory: RequestFactory, settings):
        settings.SENTRY_DSN = ''
        request = request_factory.get('/')
        handler_500(request)

        mock_render.assert_called_once_with(request, '500.html', context={}, status=500)

    # 500 handler includes Sentry event ID in context when configured
    @patch('sentry_sdk.last_event_id', return_value='abc123')
    @patch('apps.core.views.render')
    def test_with_sentry(self, mock_render, mock_event_id, request_factory: RequestFactory, settings):
        settings.SENTRY_DSN = 'https://test@sentry.io/123'
        request = request_factory.get('/')
        handler_500(request)

        mock_render.assert_called_once_with(request, '500.html', context={'sentry_event_id': 'abc123'}, status=500)


class TestCsrfFailure:
    # in-app browser detected: passes app name to template
    @patch('apps.core.views.render')
    def test_in_app_browser_detected(self, mock_render, request_factory: RequestFactory):
        request = request_factory.get('/', HTTP_USER_AGENT='Mozilla/5.0 TelegramAndroid/10.0')
        csrf_failure(request)

        mock_render.assert_called_once_with(request, '403_csrf.html', {'in_app_browser': 'Telegram'}, status=403)

    # standard browser: passes empty in_app_browser
    @patch('apps.core.views.render')
    def test_standard_browser(self, mock_render, request_factory: RequestFactory):
        request = request_factory.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; rv:128) Gecko/20100101')
        csrf_failure(request)

        mock_render.assert_called_once_with(request, '403_csrf.html', {'in_app_browser': ''}, status=403)

    # missing UA header: falls back to empty in_app_browser
    @patch('apps.core.views.render')
    def test_no_user_agent(self, mock_render, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.META.pop('HTTP_USER_AGENT', None)
        csrf_failure(request)

        mock_render.assert_called_once_with(request, '403_csrf.html', {'in_app_browser': ''}, status=403)
