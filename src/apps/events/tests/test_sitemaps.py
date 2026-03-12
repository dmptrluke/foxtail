import pytest

from ..models import Event
from ..sitemaps import EventSitemap

pytestmark = pytest.mark.django_db


class TestEventSitemap:
    # items returns all events
    def test_items(self, event: Event):
        sitemap = EventSitemap()
        assert event in sitemap.items()

    # lastmod returns the event's modified timestamp
    def test_lastmod(self, event: Event):
        sitemap = EventSitemap()
        assert sitemap.lastmod(event) == event.modified
