from datetime import timedelta

from django.test import RequestFactory
from django.utils import timezone

import pytest

from apps.blog.models import Post
from apps.blog.tests.factories import CommentFactory, PostFactory
from apps.events.models import Event, EventInterest
from apps.events.tests.factories import EventFactory
from apps.organisations.tests.factories import OrganisationFactory

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

    # homepage limits posts to 4 and events to 3
    def test_lists_capped(self, db, request_factory: RequestFactory):
        PostFactory.create_batch(5)
        EventFactory.create_batch(5)
        view = IndexView()
        view.setup(request_factory.get('/'))
        context = view.get_context_data()

        assert len(context['post_list']) <= 4
        assert len(context['event_list']) <= 3

    # structured data contains required schema.org fields
    def test_structured_data(self, settings):
        view = IndexView()
        sd = view.get_structured_data()

        assert sd['@type'] == 'WebSite'
        assert sd['url'] == f'{settings.SITE_URL}/'
        assert 'name' in sd


class TestHomepageRedesignContext:
    """Homepage provides 4 posts, featured orgs, and annotated comment counts."""

    # homepage returns max 4 posts (1 featured + 3 list)
    def test_posts_capped_at_four(self, client):
        PostFactory.create_batch(6)
        response = client.get('/')
        assert len(response.context['post_list']) == 4

    # featured post context var is the first (newest) post
    def test_featured_post_is_first(self, client):
        PostFactory.create_batch(4)
        response = client.get('/')
        assert response.context['featured_post'] == response.context['post_list'][0]

    # comment count annotation filters to approved only
    def test_posts_annotated_with_comment_count(self, client, post):
        CommentFactory(post=post, approved=True)
        CommentFactory(post=post, approved=True)
        CommentFactory(post=post, approved=False)
        response = client.get('/')
        featured = response.context['featured_post']
        assert featured.comment_count == 2

    # only featured=True organisations appear
    def test_featured_orgs_in_context(self, client, post, organisation):
        organisation.featured = True
        organisation.save()
        OrganisationFactory()  # not featured
        response = client.get('/')
        assert list(response.context['featured_organisations']) == [organisation]

    # stats context includes member count
    def test_community_stats(self, client, user, post):
        response = client.get('/')
        assert 'stats' in response.context
        assert response.context['stats']['member_count'] >= 1

    # homepage renders without errors when no posts or events exist
    def test_empty_homepage(self, client):
        response = client.get('/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestHomepageRendering:
    """Homepage renders all sections correctly for both auth states."""

    # logged-out view shows split hero with community tagline and join CTA
    def test_logged_out_shows_split_hero(self, client, post):
        response = client.get('/')
        content = response.content.decode()
        assert "New Zealand's Furry Community" in content
        assert 'Join the community' in content

    # logged-out view includes onboarding section for new visitors
    def test_logged_out_shows_onboarding(self, client, post):
        response = client.get('/')
        content = response.content.decode()
        assert 'What is furry?' in content

    # logged-in view shows personalised welcome banner
    def test_logged_in_shows_banner(self, client, user, post):
        client.force_login(user)
        response = client.get('/')
        content = response.content.decode()
        assert 'Welcome back' in content

    # logged-in view hides onboarding section (already a member)
    def test_logged_in_hides_onboarding(self, client, user, post):
        client.force_login(user)
        response = client.get('/')
        content = response.content.decode()
        assert 'What is furry?' not in content

    # event interest count is rendered on the homepage event card
    def test_events_with_interest_counts(self, client, event, user):
        EventInterest.objects.create(event=event, user=user)
        response = client.get('/')
        content = response.content.decode()
        assert '1 interested' in content

    # featured organisations are rendered by name on the homepage
    def test_featured_orgs_shown(self, client, post, organisation):
        organisation.featured = True
        organisation.save()
        response = client.get('/')
        content = response.content.decode()
        assert organisation.name in content

    # connect section lists both Telegram and Discord community links
    def test_connect_section_rendered(self, client, post):
        response = client.get('/')
        content = response.content.decode()
        assert 'Telegram' in content
        assert 'Discord' in content

    # blog post cards show reading time estimate
    def test_reading_time_shown(self, client, post):
        response = client.get('/')
        content = response.content.decode()
        assert 'min read' in content


class TestPageView:
    """Test PageView detail context."""

    # page object is passed through to template context
    def test_context_contains_page(self, page: Page, request_factory: RequestFactory):
        view = PageView()
        view.object = page
        view.setup(request_factory.get(f'/{page.slug}/'))
        context = view.get_context_data()

        assert context['page'] == page
