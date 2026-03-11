from datetime import UTC, date, time, timedelta

from django.utils.timezone import now

import pytest

from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventIsEnded:
    """Test Event.is_ended across all date/time branches."""

    # event with past end date and no end time is ended
    def test_past_end_date(self, event: Event):
        event.end = date(2019, 12, 2)
        assert event.is_ended is True

    # event with past end date and past end time is ended
    def test_past_end_date_with_time(self, event: Event):
        event.end = date(2019, 12, 2)
        event.end_time = time(12, 30, 0, tzinfo=UTC)
        assert event.is_ended is True

    # event with no end date uses start + 1 day as the boundary
    def test_no_end_date_past_start(self, event: Event):
        event.start = now().date() - timedelta(days=5)
        event.end = None
        event.end_time = None
        assert event.is_ended is True

    # event with no end date but an end time uses start + end_time
    def test_no_end_date_with_past_end_time(self, event: Event):
        event.start = now().date() - timedelta(days=1)
        event.end = None
        event.end_time = time(0, 0, 0, tzinfo=UTC)
        assert event.is_ended is True

    # future event is not ended
    def test_future_event_not_ended(self, event: Event):
        event.start = now().date() + timedelta(days=30)
        event.end = None
        event.end_time = None
        assert event.is_ended is False

    # event with future end date is not ended even if start is past
    def test_future_end_date_not_ended(self, event: Event):
        event.start = now().date() - timedelta(days=2)
        event.end = now().date() + timedelta(days=5)
        assert event.is_ended is False


class TestEventStructuredData:
    """Test Event.structured_data schema.org output."""

    # base fields are always present
    def test_required_fields(self, event: Event):
        sd = event.structured_data
        assert sd['@type'] == 'Event'
        assert sd['name'] == event.title
        assert sd['startDate'] == event.start
        assert 'url' in sd

    # endDate is included only when end is set
    def test_end_date_included(self, event: Event):
        event.end = date(2026, 6, 15)
        # clear cached_property so it recomputes
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        assert sd['endDate'] == date(2026, 6, 15)

    # endDate is absent when end is not set
    def test_end_date_absent(self, event: Event):
        event.end = None
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        assert 'endDate' not in sd

    # location uses address when available, falls back to location name
    def test_location_address_fallback(self, event: Event):
        event.location = 'Test Venue'
        event.address = ''
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        assert sd['location']['address'] == 'Test Venue'

    # location uses address when provided
    def test_location_with_address(self, event: Event):
        event.location = 'Test Venue'
        event.address = '123 Main St'
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        assert sd['location']['address'] == '123 Main St'

    # geo coordinates included when lat/lng are set
    def test_geo_included(self, event: Event):
        from decimal import Decimal

        event.location = 'Test Venue'
        event.latitude = Decimal('-41.286460')
        event.longitude = Decimal('174.776236')
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        geo = sd['location']['geo']
        assert geo['@type'] == 'GeoCoordinates'
        assert geo['latitude'] == pytest.approx(-41.28646)
        assert geo['longitude'] == pytest.approx(174.776236)

    # geo coordinates omitted when lat/lng are null
    def test_geo_omitted(self, event: Event):
        event.location = 'Test Venue'
        event.latitude = None
        event.longitude = None
        if 'structured_data' in event.__dict__:
            del event.__dict__['structured_data']
        sd = event.structured_data
        assert 'geo' not in sd['location']


class TestEvent:
    """Test Event model basics."""

    # __str__ returns the title
    def test_str(self, event: Event):
        assert str(event) == event.title

    # get_absolute_url includes year and slug
    def test_get_absolute_url(self, event: Event):
        assert event.get_absolute_url() == f'/events/{event.start.year}/{event.slug}/'
