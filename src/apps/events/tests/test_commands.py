from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError

import pytest

from ..models import Event

pytestmark = pytest.mark.django_db


class TestRefreshMaps:
    # raises error when API key is not set
    def test_no_api_key(self, settings):
        settings.MAPTILER_API_KEY = ''
        with pytest.raises(CommandError, match='MAPTILER_API_KEY'):
            call_command('refresh_maps')

    # geocodes events with addresses and updates coordinates
    @patch(
        'apps.events.management.commands.refresh_maps.geocode',
        return_value=(Decimal('-41.286460'), Decimal('174.776236')),
    )
    def test_geocodes_events(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.address = '123 Main St'
        event.save()
        out = StringIO()
        call_command('refresh_maps', stdout=out)
        event.refresh_from_db()
        assert event.latitude == Decimal('-41.286460')
        assert event.longitude == Decimal('174.776236')
        assert 'geocoded' in out.getvalue()

    # skips events with no address
    @patch('apps.events.management.commands.refresh_maps.geocode')
    def test_skips_empty_address(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.address = ''
        event.save()
        out = StringIO()
        call_command('refresh_maps', stdout=out)
        mock_geocode.assert_not_called()

    # handles geocoding failure gracefully
    @patch('apps.events.management.commands.refresh_maps.geocode', return_value=None)
    def test_geocode_failure(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.address = 'Nowhere'
        event.save()
        out = StringIO()
        call_command('refresh_maps', stdout=out)
        assert 'geocode failed' in out.getvalue()

    # --event flag filters to a single event
    @patch('apps.events.management.commands.refresh_maps.geocode', return_value=(Decimal('-41.0'), Decimal('174.0')))
    def test_single_event_filter(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.address = 'Test Address'
        event.save()
        out = StringIO()
        call_command('refresh_maps', event=event.pk, stdout=out)
        mock_geocode.assert_called_once()
        assert 'geocoded' in out.getvalue()
