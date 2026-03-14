from decimal import Decimal
from unittest.mock import patch

import pytest

from ..models import Event
from ..tasks import geocode_event

pytestmark = pytest.mark.django_db


class TestGeocodeEvent:
    # successful geocoding saves coordinates to the event
    @patch('apps.events.maptiler.geocode', return_value=(Decimal('-41.286460'), Decimal('174.776236')))
    def test_saves_coords_on_success(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        geocode_event(event.pk, '123 Main St, Wellington')
        event.refresh_from_db()
        assert event.latitude == Decimal('-41.286460')
        assert event.longitude == Decimal('174.776236')
        mock_geocode.assert_called_once_with('123 Main St, Wellington', 'test-key')

    # failed geocoding does not overwrite existing coordinates
    @patch('apps.events.maptiler.geocode', return_value=None)
    def test_no_coords_on_failure(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.latitude = Decimal('-36.0')
        event.longitude = Decimal('175.0')
        event.save()
        geocode_event(event.pk, 'Nowhere')
        event.refresh_from_db()
        assert event.latitude == Decimal('-36.0')
        assert event.longitude == Decimal('175.0')

    # missing API key skips geocoding entirely
    @patch('apps.events.maptiler.geocode')
    def test_skips_without_api_key(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = ''
        geocode_event(event.pk, '123 Main St')
        mock_geocode.assert_not_called()

    # deleted event doesn't raise
    @patch('apps.events.maptiler.geocode')
    def test_handles_deleted_event(self, mock_geocode, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        geocode_event(99999, '123 Main St')
        mock_geocode.assert_not_called()
