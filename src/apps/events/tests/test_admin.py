from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from ..admin import EventAdmin
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventAdmin:
    # tag_list returns sorted, comma-separated tag names
    def test_tag_list(self, event: Event):
        event.tags.set(['zebra', 'alpha', 'middle'])
        result = EventAdmin.tag_list(event)
        assert result == 'alpha, middle, zebra'

    # get_queryset prefetches tags (no N+1)
    def test_get_queryset_prefetches_tags(self, event: Event):
        admin = EventAdmin(Event, None)
        request = MagicMock()
        qs = admin.get_queryset(request)
        assert 'tags' in qs._prefetch_related_lookups

    # save_model geocodes when API key set and address changed
    @patch('apps.events.maptiler.geocode', return_value=(Decimal('-41.286460'), Decimal('174.776236')))
    def test_save_model_geocodes(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['address']
        event.address = '123 Main St, Wellington'
        admin.save_model(request, event, form, change=True)
        mock_geocode.assert_called_once_with('123 Main St, Wellington', 'test-key')
        assert event.latitude == Decimal('-41.286460')
        assert event.longitude == Decimal('174.776236')

    # save_model warns when geocoding fails
    @patch('apps.events.admin.messages')
    @patch('apps.events.maptiler.geocode', return_value=None)
    def test_save_model_geocode_failure_warns(self, mock_geocode, mock_messages, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['address']
        event.address = 'Nowhere'
        admin.save_model(request, event, form, change=True)
        mock_geocode.assert_called_once()
        mock_messages.warning.assert_called_once()

    # save_model clears coords when address is cleared
    @patch('apps.events.maptiler.geocode')
    def test_save_model_clears_coords(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.latitude = Decimal('-41.0')
        event.longitude = Decimal('174.0')
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['address']
        event.address = ''
        admin.save_model(request, event, form, change=True)
        assert event.latitude is None
        assert event.longitude is None
        mock_geocode.assert_not_called()

    # save_model skips geocoding when no API key
    @patch('apps.events.maptiler.geocode')
    def test_save_model_no_api_key(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = ''
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['address']
        event.address = '123 Main St'
        admin.save_model(request, event, form, change=True)
        mock_geocode.assert_not_called()

    # save_model skips geocoding when address not in changed_data
    @patch('apps.events.maptiler.geocode')
    def test_save_model_address_unchanged(self, mock_geocode, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['title']
        admin.save_model(request, event, form, change=True)
        mock_geocode.assert_not_called()
