from datetime import UTC, datetime
from urllib.parse import urlparse

from django.urls import reverse

import atoma
import pytest

from ..models import Post

pytestmark = pytest.mark.django_db


class TestLatestEntriesFeed:
    url = reverse('blog:feed')

    # feed metadata matches configured title, description, and link
    def test_feed_metadata(self, client, post: Post):
        response = client.get(self.url)
        feed = atoma.parse_rss_bytes(response.content)
        assert feed.title == 'Latest News'
        assert feed.description == 'The latest furry news.'
        assert urlparse(feed.link).path == reverse('blog:list')

    # only published posts appear in feed, ordered by date descending
    def test_published_posts_only(self, client, post: Post, second_post: Post, hidden_post: Post):
        post.created = datetime(2019, 12, 2, tzinfo=UTC)
        second_post.created = datetime(2019, 11, 1, tzinfo=UTC)
        post.save()
        second_post.save()

        response = client.get(self.url)
        feed = atoma.parse_rss_bytes(response.content)
        assert len(feed.items) == 2
        assert feed.items[0].title == post.title
        assert feed.items[1].title == second_post.title

    # feed items have correct link and publication date
    def test_item_details(self, client, post: Post):
        response = client.get(self.url)
        feed = atoma.parse_rss_bytes(response.content)
        item = feed.items[0]
        assert urlparse(item.link).path == post.get_absolute_url()
        assert item.pub_date == post.created.replace(microsecond=0)
