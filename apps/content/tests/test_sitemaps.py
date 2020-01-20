from django.contrib.auth import get_user_model
from django.contrib.sitemaps.views import sitemap
from django.test import RequestFactory
from django.urls import reverse

import pytest

from ..models import Page
from ..sitemaps import PageSitemap, StaticSitemap

pytestmark = pytest.mark.django_db


def test_static_sitemap(request_factory: RequestFactory, user: get_user_model()):
    request = request_factory.get("/sitemap.xml")
    request.user = user

    response = sitemap(request, sitemaps={
        'static': StaticSitemap
    }).render()

    assert reverse('contact:contact') in response.rendered_content
    assert response.status_code == 200


def test_page_sitemap(request_factory: RequestFactory, page: Page, user: get_user_model()):
    request = request_factory.get("/sitemap.xml")
    request.user = user

    response = sitemap(request, sitemaps={
        'pages': PageSitemap
    }).render()

    assert page.slug in response.rendered_content
    assert response.status_code == 200
