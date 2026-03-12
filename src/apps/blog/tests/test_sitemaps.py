import pytest

from ..models import Post
from ..sitemaps import PostSitemap

pytestmark = pytest.mark.django_db


class TestPostSitemap:
    # only published posts appear in sitemap
    def test_items_returns_published(self, post: Post, hidden_post: Post):
        sitemap = PostSitemap()
        items = list(sitemap.items())
        assert post in items
        assert hidden_post not in items
