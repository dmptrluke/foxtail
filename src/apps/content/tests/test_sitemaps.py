from django.contrib.auth import get_user_model
from django.contrib.sitemaps.views import sitemap
from django.test import RequestFactory
from django.urls import reverse

import pytest

from ..models import Page
from ..sitemaps import PageSitemap, StaticSitemap

pytestmark = pytest.mark.django_db


class TestStaticSitemap:
    """Test StaticSitemap includes key site URLs."""

    # static sitemap includes all registered static pages
    def test_includes_static_urls(self, request_factory: RequestFactory, user: get_user_model()):
        request = request_factory.get('/sitemap.xml')
        request.user = user
        response = sitemap(request, sitemaps={'static': StaticSitemap}).render()

        assert response.status_code == 200
        assert reverse('contact:contact') in response.rendered_content


class TestPageSitemap:
    """Test PageSitemap includes content pages."""

    # page sitemap includes created pages by slug
    def test_includes_page(self, request_factory: RequestFactory, page: Page, user: get_user_model()):
        request = request_factory.get('/sitemap.xml')
        request.user = user
        response = sitemap(request, sitemaps={'pages': PageSitemap}).render()

        assert response.status_code == 200
        assert page.slug in response.rendered_content
