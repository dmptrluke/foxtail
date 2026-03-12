from django.test import RequestFactory

from ..url_transform import url_transform


class TestUrlTransform:
    # adds a new query parameter to a URL with no existing params
    def test_adds_new_param(self, request_factory: RequestFactory):
        context = {'request': request_factory.get('/accounts/')}
        assert url_transform(context, page=1) == 'page=1'

    # replaces an existing query parameter value
    def test_replaces_existing_param(self, request_factory: RequestFactory):
        context = {'request': request_factory.get('/accounts/?page=1')}
        assert url_transform(context, page=2) == 'page=2'

    # merges a new parameter while preserving existing ones
    def test_merges_params(self, request_factory: RequestFactory):
        context = {'request': request_factory.get('/accounts/?page=2')}
        assert url_transform(context, view='list') == 'page=2&view=list'

    # removes a parameter when its value is None
    def test_clears_param_with_none(self, request_factory: RequestFactory):
        context = {'request': request_factory.get('/accounts/?page=2&view=list')}
        assert url_transform(context, view=None) == 'page=2'
