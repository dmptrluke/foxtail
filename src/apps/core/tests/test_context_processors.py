from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from ..context_processors import debug, site


class TestSiteContextProcessor:
    # includes DEFAULT_COLOR_SCHEME from settings
    def test_includes_default_color_scheme(self, request_factory: RequestFactory, settings):
        settings.DEFAULT_COLOR_SCHEME = 'plum'
        request = request_factory.get('/')
        result = site(request)

        assert result['DEFAULT_COLOR_SCHEME'] == 'plum'

    # reflects overridden DEFAULT_COLOR_SCHEME setting
    def test_default_color_scheme_reflects_setting(self, request_factory: RequestFactory, settings):
        settings.DEFAULT_COLOR_SCHEME = 'coffee'
        request = request_factory.get('/')
        result = site(request)

        assert result['DEFAULT_COLOR_SCHEME'] == 'coffee'


class TestDebugContextProcessor:
    # extracts first IP from X-Forwarded-For header
    def test_uses_forwarded_ip(self, request_factory: RequestFactory):
        request = request_factory.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 5.6.7.8')
        request.user = AnonymousUser()
        result = debug(request)

        assert result['DEBUG_DATA_IP'] == '1.2.3.4'

    # falls back to REMOTE_ADDR when no forwarded header
    def test_uses_remote_addr(self, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = AnonymousUser()
        result = debug(request)

        assert result['DEBUG_DATA_IP'] == '127.0.0.1'

    # includes truncated git SHA from settings
    def test_includes_version_from_git_sha(self, request_factory: RequestFactory, settings):
        settings.GIT_SHA = 'abc123def456'
        request = request_factory.get('/')
        request.user = AnonymousUser()
        result = debug(request)

        assert result['DEBUG_DATA_VERSION'] == 'abc123de'

    # returns empty version when GIT_SHA is blank
    def test_version_empty_without_git_sha(self, request_factory: RequestFactory, settings):
        settings.GIT_SHA = ''
        request = request_factory.get('/')
        request.user = AnonymousUser()
        result = debug(request)

        assert result['DEBUG_DATA_VERSION'] == ''
