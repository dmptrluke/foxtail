from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from ..context_processors import debug


class TestDebugContextProcessor:
    # extracts client IP from X-Forwarded-For header
    def test_uses_forwarded_ip(self, request_factory: RequestFactory):
        request = request_factory.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 5.6.7.8')
        request.user = AnonymousUser()
        result = debug(request)

        assert 'ip: 1.2.3.4' in result['DEBUG_DATA']

    # falls back to REMOTE_ADDR when no forwarded header
    def test_uses_remote_addr(self, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = AnonymousUser()
        result = debug(request)

        assert 'ip: 127.0.0.1' in result['DEBUG_DATA']

    # includes authenticated user's username
    def test_includes_username(self, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = MagicMock(is_authenticated=True, username='alice')
        result = debug(request)

        assert 'user: alice' in result['DEBUG_DATA']

    # omits user field for anonymous requests
    def test_excludes_user_when_anonymous(self, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = AnonymousUser()
        result = debug(request)

        assert 'user:' not in result['DEBUG_DATA']
