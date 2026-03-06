from datetime import datetime
from urllib.parse import urlparse

from django.urls import reverse

import atoma
import pytest
from pytz import utc

from ..models import Post

pytestmark = pytest.mark.django_db


def test_feed(client, post: Post, second_post: Post, hidden_post: Post):
    # set the post dates to they are listed in a predictable order
    post.created = datetime(2019, 12, 2, tzinfo=utc)
    second_post.created = datetime(2019, 11, 1, tzinfo=utc)

    post.save()
    second_post.save()

    # get the feed
    url = reverse('blog:feed')
    response = client.get(url)
    feed = atoma.parse_rss_bytes(response.content)

    # check the title and description match those in the config
    assert feed.title == 'Latest News'
    assert feed.description == 'The latest furry news.'

    # check the link is correct
    assert urlparse(feed.link).path == reverse('blog:list')

    # check we only have two visible items
    assert len(feed.items) == 2

    # first post
    item_one = feed.items[0]
    assert urlparse(item_one.link).path == post.get_absolute_url()
    assert item_one.title == post.title
    assert item_one.pub_date == post.created

    # second post
    item_two = feed.items[1]
    assert urlparse(item_two.link).path == second_post.get_absolute_url()
    assert item_two.title == second_post.title
    assert item_two.pub_date == second_post.created
