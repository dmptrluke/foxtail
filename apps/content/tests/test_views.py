from django.test import RequestFactory

import pytest

from apps.events.models import Event
from foxtail_blog.models import Post

from ..models import Page
from ..views import IndexView, PageView

pytestmark = pytest.mark.django_db


def test_index(post: Post, event: Event, request_factory: RequestFactory):
    view = IndexView()
    request = request_factory.get('/')

    view.setup(request)

    context = view.get_context_data()

    # there should be one post
    assert len(context['post_list']) == 1

    # the post should be correct
    post_context: Post = context['post_list'][0]
    assert post_context.title == post.title

    # there should be one event
    assert len(context['event_list']) == 1

    # the event should be correct
    event_context: Event = context['event_list'][0]
    assert event_context.title == event.title


def test_page(page: Page, request_factory: RequestFactory):
    view = PageView()
    request = request_factory.get(f'/{page.slug}/')

    view.object = page
    view.setup(request)

    context = view.get_context_data()

    # the page should be correct
    page_context: Page = context['page']
    assert page_context.title == page.title
    assert page_context.body == page.body
