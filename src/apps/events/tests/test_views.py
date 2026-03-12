from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils.timezone import now

import pytest
from published.constants import AVAILABLE

from ..models import Event
from .factories import EventFactory

pytestmark = pytest.mark.django_db


class TestEventListView:
    url = reverse('events:list')

    # published future events appear in upcoming list
    def test_upcoming_events(self, client, event: Event):
        response = client.get(self.url)
        assert response.status_code == 200
        assert event in response.context['upcoming_events']

    # published past events appear in past list
    def test_past_events(self, client, past_event: Event):
        response = client.get(self.url)
        assert response.status_code == 200
        assert past_event in response.context['past_events']

    # ongoing event (past start, future end) appears in upcoming, not past
    def test_ongoing_event_in_upcoming(self, client):
        ongoing = EventFactory(
            start=now().date() - timedelta(days=2),
            end=now().date() + timedelta(days=2),
        )
        response = client.get(self.url)
        assert ongoing in response.context['upcoming_events']
        assert ongoing not in response.context['past_events']

    # featured event is the first upcoming event
    def test_featured_event(self, client, event: Event):
        response = client.get(self.url)
        assert response.context['featured_event'] == event

    # event_years context contains distinct years
    def test_event_years(self, client, event: Event):
        response = client.get(self.url)
        assert event.start.year in response.context['event_years']


class TestEventListYearView:
    # events are filtered to the requested year
    def test_filters_by_year(self, client, event: Event):
        year = event.start.year
        response = client.get(reverse('events:list_year', kwargs={'year': year}))
        assert response.status_code == 200
        assert event in response.context['upcoming_events']
        assert response.context['year'] == str(year)

    # events from other years are excluded
    def test_excludes_other_years(self, client, event: Event):
        other_year = event.start.year + 5
        response = client.get(reverse('events:list_year', kwargs={'year': other_year}))
        assert list(response.context['upcoming_events']) == []
        assert list(response.context['past_events']) == []


class TestEventDetailView:
    # detail view renders a published event
    def test_renders_event(self, client, event: Event):
        response = client.get(event.get_absolute_url())
        assert response.status_code == 200
        assert response.context['event'] == event


class TestEventManageListView:
    url = reverse('events:manage_list')

    # regular user gets 403
    def test_requires_editor_permission(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # editor can view management list
    def test_editor_can_access(self, client, editor, event: Event):
        client.force_login(editor)
        response = client.get(self.url)
        assert response.status_code == 200
        assert event in response.context['events']


class TestEventCreateView:
    url = reverse('events:event_create')

    # regular user gets 403
    def test_requires_editor_permission(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # editor can create an event with tags, redirects to edit view
    def test_creates_event(self, client, editor):
        client.force_login(editor)
        data = {
            'title': 'New Event',
            'slug': 'new-event',
            'description': 'Event description.',
            'location': 'Wellington',
            'start': '2026-06-15',
            'publish_status': AVAILABLE,
            'tags': 'meetup, social',
            'image_ppoi': '0.5x0.5',
        }
        response = client.post(self.url, data)
        event = Event.objects.get(slug='new-event')
        assert response.status_code == 302
        assert response['Location'] == reverse('events:event_edit', kwargs={'pk': event.pk})
        assert set(event.tags.names()) == {'meetup', 'social'}
        messages = list(get_messages(response.wsgi_request))
        assert any('created' in str(m) for m in messages)

    # geocoding runs when address is provided and API key is set
    @patch('apps.events.maptiler.geocode', return_value=None)
    def test_geocoding_on_create(self, mock_geocode, client, editor, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        client.force_login(editor)
        data = {
            'title': 'Geocode Test',
            'slug': 'geocode-test',
            'description': 'Test event.',
            'location': 'Wellington',
            'address': '123 Main St, Wellington',
            'start': '2026-06-15',
            'publish_status': AVAILABLE,
            'tags': 'test',
            'image_ppoi': '0.5x0.5',
        }
        client.post(self.url, data)
        mock_geocode.assert_called_once_with('123 Main St, Wellington', 'test-key')


class TestEventUpdateView:
    # regular user gets 403
    def test_requires_editor_permission(self, client, user, event: Event):
        client.force_login(user)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        response = client.get(url)
        assert response.status_code == 403

    # editor can update an event and its tags
    def test_updates_event(self, client, editor, event: Event):
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': 'Updated Title',
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': 'edited',
            'image_ppoi': '0.5x0.5',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        event.refresh_from_db()
        assert event.title == 'Updated Title'
        assert list(event.tags.names()) == ['edited']
        messages = list(get_messages(response.wsgi_request))
        assert any('saved' in str(m) for m in messages)

    # successful geocoding sets lat/lng on the event
    @patch('apps.events.maptiler.geocode')
    def test_geocoding_success_sets_coords(self, mock_geocode, client, editor, event: Event, settings):
        mock_geocode.return_value = (Decimal('-41.286460'), Decimal('174.776236'))
        settings.MAPTILER_API_KEY = 'test-key'
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'address': 'TSB Arena, Wellington',
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
        }
        client.post(url, data)
        event.refresh_from_db()
        assert event.latitude == Decimal('-41.286460')
        assert event.longitude == Decimal('174.776236')

    # geocoding runs when address is changed
    @patch('apps.events.maptiler.geocode', return_value=None)
    def test_geocoding_on_address_change(self, mock_geocode, client, editor, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'address': 'New Address, Wellington',
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
        }
        client.post(url, data)
        mock_geocode.assert_called_once_with('New Address, Wellington', 'test-key')

    # clearing address clears lat/lng without calling geocode
    @patch('apps.events.maptiler.geocode')
    def test_clearing_address_clears_coords(self, mock_geocode, client, editor, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        event.address = 'Old Address'
        event.latitude = -41.0
        event.longitude = 174.0
        event.save()
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'address': '',
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
        }
        client.post(url, data)
        event.refresh_from_db()
        assert event.latitude is None
        assert event.longitude is None
        mock_geocode.assert_not_called()

    # failed geocoding shows warning message
    @patch('apps.events.maptiler.geocode', return_value=None)
    def test_geocoding_failure_shows_warning(self, mock_geocode, client, editor, event: Event, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'address': 'Nowhere Special',
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any('geocoded' in str(m) for m in messages)


class TestEventDeleteView:
    # regular user gets 403
    def test_requires_editor_permission(self, client, user, event: Event):
        client.force_login(user)
        url = reverse('events:event_delete', kwargs={'pk': event.pk})
        response = client.post(url)
        assert response.status_code == 403

    # editor can delete an event with success message
    def test_deletes_event(self, client, editor, event: Event):
        client.force_login(editor)
        url = reverse('events:event_delete', kwargs={'pk': event.pk})
        title = event.title
        response = client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('events:manage_list')
        assert not Event.objects.filter(pk=event.pk).exists()
        messages = list(get_messages(response.wsgi_request))
        assert any(title in str(m) for m in messages)
