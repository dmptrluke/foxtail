import json

from django.http import Http404
from django.test import RequestFactory

import pytest

from apps.core.views import ApiView


class ConcreteApiView(ApiView):
    def get(self, request):
        return self.success({'ok': True})

    def post(self, request):
        return self.success({'data': self.data.get('key')})


class RaisingNotFoundView(ApiView):
    def get(self, request):
        raise Http404


class RaisingForbiddenView(ApiView):
    def get(self, request):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied


class RaisingErrorView(ApiView):
    def get(self, request):
        raise RuntimeError('unexpected')


class PublicApiView(ApiView):
    require_auth = False

    def get(self, request):
        return self.success({'public': True})


@pytest.mark.django_db
class TestApiView:
    """Test ApiView base class."""

    # authenticated requests succeed
    def test_authenticated_request(self, user, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = user
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {'ok': True}

    # unauthenticated requests return 403 JSON
    def test_unauthenticated_returns_403(self, request_factory: RequestFactory):
        from django.contrib.auth.models import AnonymousUser

        request = request_factory.get('/')
        request.user = AnonymousUser()
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 403
        assert json.loads(response.content)['error'] == 'Authentication required'

    # require_auth=False allows anonymous access
    def test_public_view(self, request_factory: RequestFactory):
        from django.contrib.auth.models import AnonymousUser

        request = request_factory.get('/')
        request.user = AnonymousUser()
        response = PublicApiView.as_view()(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {'public': True}

    # disallowed methods return 405 JSON
    def test_method_not_allowed(self, user, request_factory: RequestFactory):
        request = request_factory.delete('/')
        request.user = user
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 405
        assert json.loads(response.content)['error'] == 'Method not allowed'

    # Http404 is caught and returned as JSON
    def test_404_returns_json(self, user, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = user
        response = RaisingNotFoundView.as_view()(request)
        assert response.status_code == 404
        assert json.loads(response.content)['error'] == 'Not found'

    # PermissionDenied is caught and returned as JSON
    def test_403_returns_json(self, user, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = user
        response = RaisingForbiddenView.as_view()(request)
        assert response.status_code == 403
        assert json.loads(response.content)['error'] == 'Forbidden'

    # unhandled exceptions return JSON 500
    def test_500_returns_json(self, user, request_factory: RequestFactory):
        request = request_factory.get('/')
        request.user = user
        response = RaisingErrorView.as_view()(request)
        assert response.status_code == 500
        assert json.loads(response.content)['error'] == 'Internal server error'

    # self.data parses JSON request body
    def test_json_body_parsing(self, user, request_factory: RequestFactory):
        request = request_factory.post('/', json.dumps({'key': 'value'}), content_type='application/json')
        request.user = user
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 200
        assert json.loads(response.content)['data'] == 'value'

    # self.data falls back to request.POST for form-encoded
    def test_form_body_parsing(self, user, request_factory: RequestFactory):
        request = request_factory.post('/', {'key': 'value'})
        request.user = user
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 200
        assert json.loads(response.content)['data'] == 'value'

    # malformed JSON returns empty dict (not a crash)
    def test_malformed_json(self, user, request_factory: RequestFactory):
        request = request_factory.post('/', 'not json', content_type='application/json')
        request.user = user
        response = ConcreteApiView.as_view()(request)
        assert response.status_code == 200
        assert json.loads(response.content)['data'] is None
