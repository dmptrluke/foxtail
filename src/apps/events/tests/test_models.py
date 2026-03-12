from datetime import UTC, date, time, timedelta
from decimal import Decimal
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now

import pytest

from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventIsEnded:
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
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert sd['endDate'] == date(2026, 6, 15)

    # endDate is absent when end is not set
    def test_end_date_absent(self, event: Event):
        event.end = None
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert 'endDate' not in sd

    # location uses address when available, falls back to location name
    def test_location_address_fallback(self, event: Event):
        event.location = 'Test Venue'
        event.address = ''
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert sd['location']['address'] == 'Test Venue'

    # location uses address when provided
    def test_location_with_address(self, event: Event):
        event.location = 'Test Venue'
        event.address = '123 Main St'
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert sd['location']['address'] == '123 Main St'

    # geo coordinates included when lat/lng are set
    def test_geo_included(self, event: Event):
        event.location = 'Test Venue'
        event.latitude = Decimal('-41.286460')
        event.longitude = Decimal('174.776236')
        event.__dict__.pop('structured_data', None)
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
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert 'geo' not in sd['location']

    # location block absent when location is empty
    def test_no_location(self, event: Event):
        event.location = ''
        event.__dict__.pop('structured_data', None)
        sd = event.structured_data
        assert 'location' not in sd

    # relative image URL gets SITE_URL prepended
    def test_image_relative_url(self, event: Event):
        with patch.object(type(event), 'image', new_callable=PropertyMock) as mock_image:
            mock_obj = mock_image.return_value
            mock_obj.card_2x = '/media/events/test.jpg'
            event.__dict__.pop('structured_data', None)
            sd = event.structured_data
            assert sd['image']['@type'] == 'ImageObject'
            assert sd['image']['url'] == f'{settings.SITE_URL}/media/events/test.jpg'
            assert sd['image']['width'] == 1200
            assert sd['image']['height'] == 630

    # absolute image URL used as-is
    def test_image_absolute_url(self, event: Event):
        with patch.object(type(event), 'image', new_callable=PropertyMock) as mock_image:
            mock_obj = mock_image.return_value
            mock_obj.card_2x = 'https://cdn.example.com/events/test.jpg'
            event.__dict__.pop('structured_data', None)
            sd = event.structured_data
            assert sd['image']['url'] == 'https://cdn.example.com/events/test.jpg'

    # no image block when event has no image
    def test_without_image(self, event: Event):
        sd = event.structured_data
        assert 'image' not in sd


class TestEvent:
    # __str__ returns the title
    def test_str(self, event: Event):
        assert str(event) == event.title

    # get_absolute_url includes year and slug
    def test_get_absolute_url(self, event: Event):
        assert event.get_absolute_url() == f'/events/{event.start.year}/{event.slug}/'

    # clean() raises ValidationError when end date is before start date
    def test_clean_end_before_start(self, event: Event):
        event.start = date(2026, 6, 15)
        event.end = date(2026, 6, 10)
        with pytest.raises(ValidationError, match='End date cannot be before start date'):
            event.clean()

    # clean() passes when end date is after start date
    def test_clean_valid_dates(self, event: Event):
        event.start = date(2026, 6, 15)
        event.end = date(2026, 6, 20)
        event.clean()
