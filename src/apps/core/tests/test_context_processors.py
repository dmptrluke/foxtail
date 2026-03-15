from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from ..context_processors import debug


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
