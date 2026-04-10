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

    # content type is Atom XML
    def test_content_type(self, client, post: Post):
        response = client.get(self.url)
        assert 'application/atom+xml' in response['Content-Type']

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

    # summary uses the post's description field when set
    def test_item_summary_from_field(self, client, post: Post):
        post.description = 'A short summary.'
        post.save()
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        assert feed.entries[0].summary == 'A short summary.'

    # summary falls back to truncated body when description field is empty
    def test_item_summary_fallback(self, client, post: Post):
        post.description = ''
        post.save()
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        assert len(feed.entries[0].summary) <= 203  # 200 chars + ellipsis

    # full HTML content in <content> element
    def test_content_html(self, client, post: Post):
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        entry = feed.entries[0]
        assert entry.get('content')
        assert post.text_rendered.strip() in entry.content[0].value

    # author name included when post has an author
    def test_item_author(self, client, post: Post):
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        assert feed.entries[0].get('author') == post.author.name

    # tags mapped to Atom categories
    def test_item_categories(self, client, post: Post):
        post.tags.add('testing', 'rss')
        response = client.get(self.url)
        feed = feedparser.parse(response.content)
        tags = {t.term for t in feed.entries[0].tags}
        assert 'testing' in tags
        assert 'rss' in tags

    # webfeeds namespace declared in feed XML
    def test_webfeeds_namespace(self, client, post: Post):
        response = client.get(self.url)
        assert b'xmlns:webfeeds=' in response.content

    # webfeeds accent color present
    def test_webfeeds_accent_color(self, client, post: Post):
        response = client.get(self.url)
        assert b'<webfeeds:accentColor>281e33</webfeeds:accentColor>' in response.content
