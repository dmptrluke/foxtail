from datetime import UTC, datetime
from urllib.parse import urlparse

from django.urls import reverse

import feedparser
import pytest

from ..models import Post

pytestmark = pytest.mark.django_db


class TestLatestEntriesFeed:
    url = reverse('blog:feed')

    # feed metadata matches configured title, description, and link
    def test_feed_metadata(self, client, post: Post):
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        assert feed.feed.title == 'Latest News'
        assert feed.feed.subtitle == 'The latest furry news.'
        assert urlparse(feed.feed.link).path == reverse('blog:list')

    # only published posts appear in feed, ordered by date descending
    def test_published_posts_only(self, client, post: Post, second_post: Post, hidden_post: Post):
        post.created = datetime(2019, 12, 2, tzinfo=UTC)
        second_post.created = datetime(2019, 11, 1, tzinfo=UTC)
        post.save()
        second_post.save()

        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        assert len(feed.entries) == 2
        assert feed.entries[0].title == post.title
        assert feed.entries[1].title == second_post.title

    # feed items have correct link and publication date
    def test_item_details(self, client, post: Post):
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        entry = feed.entries[0]
        assert urlparse(entry.link).path == post.get_absolute_url()
        expected = post.created.replace(microsecond=0)
        assert datetime(*entry.published_parsed[:6], tzinfo=UTC) == expected
