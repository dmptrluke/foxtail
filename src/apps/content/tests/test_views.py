from datetime import timedelta

from django.test import RequestFactory
from django.utils import timezone

import pytest

from apps.blog.models import Post
from apps.blog.tests.factories import PostFactory
from apps.events.models import Event
from apps.events.tests.factories import EventFactory

from ..models import Page
from ..views import IndexView, PageView

pytestmark = pytest.mark.django_db


class TestIndexView:
    """Test IndexView homepage context and structured data."""

    # published posts appear in context, hidden posts are excluded
    def test_post_list_excludes_hidden(self, post: Post, hidden_post: Post, request_factory: RequestFactory):
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert list(context['post_list']) == [post]

    # upcoming events appear in context
    def test_event_list_includes_future(self, event: Event, request_factory: RequestFactory):
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert list(context['event_list']) == [event]

    # past events are excluded from the homepage
    def test_event_list_excludes_past(self, past_event: Event, request_factory: RequestFactory):
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert list(context['event_list']) == []

    # multi-day event with past start but future end still appears (end >= today branch)
    def test_event_list_includes_ongoing(self, db, request_factory: RequestFactory):
        ongoing = EventFactory(
            start=timezone.now().date() - timedelta(days=2),
            end=timezone.now().date() + timedelta(days=2),
        )
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert ongoing in context['event_list']

    # homepage limits posts and events to 3 each
    def test_lists_capped_at_three(self, db, request_factory: RequestFactory):
        PostFactory.create_batch(5)
        EventFactory.create_batch(5)
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert len(context['post_list']) <= 3
        assert len(context['event_list']) <= 3

    # structured data contains required schema.org fields
    def test_structured_data(self, settings):
        view = IndexView()
        sd = view.get_structured_data()

        assert sd['@type'] == 'WebSite'
        assert sd['url'] == f'{settings.SITE_URL}/'
        assert 'name' in sd


class TestPageView:
    """Test PageView detail context."""

    # page object is passed through to template context
    def test_context_contains_page(self, page: Page, request_factory: RequestFactory):
        view = PageView()
        view.object = page
        view.setup(request_factory.get(f'/{page.slug}/'))
        context = view.get_context_data()

        assert context['page'] == page
