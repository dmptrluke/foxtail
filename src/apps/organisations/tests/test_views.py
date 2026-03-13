from datetime import timedelta

from django.utils.timezone import now

import pytest

from apps.events.tests.factories import EventFactory

from .factories import EventSeriesFactory, OrganisationFactory, SocialLinkFactory

pytestmark = pytest.mark.django_db


class TestOrganisationDetailView:
    # detail view renders an organisation page
    def test_renders_organisation(self, client):
        org = OrganisationFactory()
        response = client.get(org.get_absolute_url())
        assert response.status_code == 200
        assert response.context['organisation'] == org

    # social_links are included in context
    def test_context_includes_social_links(self, client):
        org = OrganisationFactory()
        link = SocialLinkFactory(organisation=org, platform='discord')
        response = client.get(org.get_absolute_url())
        assert link in response.context['social_links']

    # next_event is the nearest upcoming event for this org
    def test_next_event_upcoming(self, client):
        org = OrganisationFactory()
        future = EventFactory(organisation=org, start=now().date() + timedelta(days=10))
        EventFactory(organisation=org, start=now().date() + timedelta(days=30))
        response = client.get(org.get_absolute_url())
        assert response.context['next_event'] == future

    # next_event is None when org has no upcoming events
    def test_next_event_none_when_all_past(self, client):
        org = OrganisationFactory()
        EventFactory(organisation=org, start=now().date() - timedelta(days=30))
        response = client.get(org.get_absolute_url())
        assert response.context['next_event'] is None

    # events from series-linked events appear in context
    def test_events_include_series_linked(self, client):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory(series=series, organisation=None)
        response = client.get(org.get_absolute_url())
        assert event in response.context['events']

    # series are included in context
    def test_context_includes_series(self, client):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        response = client.get(org.get_absolute_url())
        assert series in response.context['series']

    # events are ordered by series name (nulls last), then by start descending
    def test_events_ordered_by_series_then_start(self, client):
        org = OrganisationFactory()
        series_b = EventSeriesFactory(name='Beta', organisation=org)
        series_a = EventSeriesFactory(name='Alpha', organisation=org)
        ev_a = EventFactory(series=series_a, organisation=None, start=now().date() + timedelta(days=5))
        ev_b = EventFactory(series=series_b, organisation=None, start=now().date() + timedelta(days=10))
        ev_none = EventFactory(organisation=org, series=None, start=now().date() + timedelta(days=1))
        response = client.get(org.get_absolute_url())
        events = list(response.context['events'])
        assert events == [ev_a, ev_b, ev_none]


class TestEventSeriesDetailView:
    # detail view renders an event series page
    def test_renders_series(self, client):
        series = EventSeriesFactory()
        response = client.get(series.get_absolute_url())
        assert response.status_code == 200
        assert response.context['eventseries'] == series

    # events belonging to the series appear in context
    def test_context_includes_events(self, client):
        series = EventSeriesFactory()
        event = EventFactory(series=series)
        other = EventFactory()
        response = client.get(series.get_absolute_url())
        assert event in response.context['events']
        assert other not in response.context['events']
