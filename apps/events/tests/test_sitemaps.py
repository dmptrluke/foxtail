from django.contrib.auth import get_user_model
from django.contrib.sitemaps.views import sitemap
from django.test import RequestFactory

import pytest

from ..models import Event
from ..sitemaps import EventSitemap

pytestmark = pytest.mark.django_db


def test_event_sitemap(request_factory: RequestFactory, event: Event, user: get_user_model()):
    request = request_factory.get("/sitemap.xml")
    request.user = user

    response = sitemap(request, sitemaps={
        'events': EventSitemap
    }).render()

    assert event.slug in response.rendered_content
    assert response.status_code == 200
