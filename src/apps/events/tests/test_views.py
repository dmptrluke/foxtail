from datetime import timedelta

from django.http import Http404
from django.test import RequestFactory
from django.utils.timezone import now

import pytest

from ..models import Event
from ..views import EventDetail, EventList, EventListYear
from .factories import EventFactory

pytestmark = pytest.mark.django_db


class TestEventList:
    """Test EventList upcoming/past split."""

    # future events appear in upcoming, past events appear in past
    def test_upcoming_and_past_split(self, event: Event, past_event: Event, request_factory: RequestFactory):
        view = EventList()
        view.setup(request_factory.get('/events/'))
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert list(context['upcoming_events']) == [event]
        assert list(context['past_events']) == [past_event]

    # ongoing event with past start but future end appears in upcoming, not past
    def test_ongoing_event_in_upcoming(self, db, request_factory: RequestFactory):
        ongoing = EventFactory(
            start=now().date() - timedelta(days=2),
            end=now().date() + timedelta(days=2),
        )
        view = EventList()
        view.setup(request_factory.get('/events/'))
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert ongoing in context['upcoming_events']
        assert ongoing not in context['past_events']


class TestEventListYear:
    """Test EventListYear year-scoped filtering."""

    # events are filtered to the requested year
    def test_filters_by_year(self, db, request_factory: RequestFactory):
        this_year = now().date().year
        event = EventFactory(start=now().date() + timedelta(days=30))
        view = EventListYear()
        view.setup(request_factory.get(f'/events/{this_year}/'))
        view.kwargs = {'year': str(this_year)}
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert event in context['upcoming_events']
        assert context['year'] == str(this_year)

    # events from other years are excluded
    def test_excludes_other_years(self, db, request_factory: RequestFactory):
        this_year = now().date().year
        other_year = this_year + 2
        EventFactory(start=now().date() + timedelta(days=30))
        view = EventListYear()
        view.setup(request_factory.get(f'/events/{other_year}/'))
        view.kwargs = {'year': str(other_year)}
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert list(context['upcoming_events']) == []
        assert list(context['past_events']) == []

    # invalid year raises 404
    def test_invalid_year_404(self, db, request_factory: RequestFactory):
        view = EventListYear()
        view.setup(request_factory.get('/events/notayear/'))
        view.kwargs = {'year': 'notayear'}
        view.object_list = view.get_queryset()

        with pytest.raises(Http404):
            view.get_context_data()


class TestEventDetail:
    """Test EventDetail year+slug lookup."""

    # detail view finds event by year and slug
    def test_finds_event(self, event: Event, request_factory: RequestFactory):
        view = EventDetail()
        view.setup(request_factory.get(event.get_absolute_url()))
        view.kwargs = {'year': str(event.start.year), 'slug': event.slug}
        qs = view.get_queryset()

        assert list(qs) == [event]

    # invalid year raises 404
    def test_invalid_year_404(self, event: Event, request_factory: RequestFactory):
        view = EventDetail()
        view.setup(request_factory.get('/events/notayear/test/'))
        view.kwargs = {'year': 'notayear', 'slug': event.slug}

        with pytest.raises(Http404):
            view.get_queryset()
