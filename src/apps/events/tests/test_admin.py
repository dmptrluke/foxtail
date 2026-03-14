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

    # save_model enqueues geocoding task when address changed
    @patch('apps.events.admin.transaction.on_commit', lambda fn: fn())
    @patch('apps.events.admin.geocode_event')
    def test_save_model_enqueues_geocoding(self, mock_task, event: Event):
        event.latitude = Decimal('-41.0')
        event.longitude = Decimal('174.0')
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['address']
        event.address = '123 Main St, Wellington'
        admin.save_model(request, event, form, change=True)
        mock_task.assert_called_once_with(event.pk, '123 Main St, Wellington')
        assert event.latitude is None
        assert event.longitude is None

    # save_model clears coords when address is cleared
    @patch('apps.events.admin.geocode_event')
    def test_save_model_clears_coords(self, mock_task, event: Event):
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
        mock_task.assert_not_called()

    # save_model skips geocoding when address not in changed_data
    @patch('apps.events.admin.geocode_event')
    def test_save_model_address_unchanged(self, mock_task, event: Event):
        admin = EventAdmin(Event, None)
        request = MagicMock()
        form = MagicMock()
        form.changed_data = ['title']
        admin.save_model(request, event, form, change=True)
        mock_task.assert_not_called()
