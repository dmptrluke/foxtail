from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils.timezone import now

import pytest
from published.constants import AVAILABLE

from ..models import Event, EventTicketTier
from .factories import EventFactory, EventInterestFactory, EventTicketTierFactory

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

    # show_series is True when event has a series
    def test_show_series_with_series(self, client):
        from apps.organisations.tests.factories import EventSeriesFactory

        series = EventSeriesFactory(name='Cool Series')
        event = EventFactory(series=series, organisation=None)
        response = client.get(event.get_absolute_url())
        assert response.context['show_series'] is True

    # show_series is False when event has no series
    def test_show_series_without_series(self, client, event: Event):
        response = client.get(event.get_absolute_url())
        assert response.context['show_series'] is False

    # series pill hidden when series name matches org name and org has only that series
    def test_show_series_hidden_when_redundant(self, client):
        from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

        org = OrganisationFactory(name='Wellington Furries')
        series = EventSeriesFactory(name='Wellington Furries', organisation=org)
        event = EventFactory(series=series, organisation=None)
        response = client.get(event.get_absolute_url())
        assert response.context['show_series'] is False

    # series pill shown when series name differs from org name
    def test_show_series_visible_when_name_differs(self, client):
        from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

        org = OrganisationFactory(name='Wellington Furries')
        series = EventSeriesFactory(name='Monthly Meets', organisation=org)
        event = EventFactory(series=series, organisation=None)
        response = client.get(event.get_absolute_url())
        assert response.context['show_series'] is True

    # series pill shown when org has multiple series (even if one name matches)
    def test_show_series_visible_when_org_has_multiple_series(self, client):
        from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

        org = OrganisationFactory(name='Wellington Furries')
        series = EventSeriesFactory(name='Wellington Furries', organisation=org)
        EventSeriesFactory(name='Annual Con', organisation=org)
        event = EventFactory(series=series, organisation=None)
        response = client.get(event.get_absolute_url())
        assert response.context['show_series'] is True

    # authenticated user sees their interest status
    def test_interest_status_authenticated(self, client, user):
        event = EventFactory()
        EventInterestFactory(event=event, user=user, status='going')
        client.force_login(user)
        response = client.get(event.get_absolute_url())
        assert response.context['user_interest_status'] == 'going'

    # authenticated user with no interest gets empty string
    def test_interest_status_empty(self, client, user):
        event = EventFactory()
        client.force_login(user)
        response = client.get(event.get_absolute_url())
        assert response.context['user_interest_status'] == ''

    # anonymous user has no interest status in context
    def test_interest_status_anonymous(self, client):
        event = EventFactory()
        response = client.get(event.get_absolute_url())
        assert 'user_interest_status' not in response.context

    # pricing is hidden when an event has no ticket tiers
    def test_pricing_hidden_without_tiers(self, client, event: Event):
        response = client.get(event.get_absolute_url())
        assert b'Pricing' not in response.content

    # pricing shows ticket tier names, prices, and availability labels
    def test_pricing_renders_tiers(self, client):
        event = EventFactory()
        EventTicketTierFactory(
            event=event,
            name='Early bird',
            price=Decimal('25.00'),
            currency='AUD',
            available_from=now() + timedelta(days=1),
        )
        response = client.get(event.get_absolute_url())
        assert b'Pricing' in response.content
        assert b'Early bird' in response.content
        assert b'AUD 25.00' in response.content
        assert b'Opens' in response.content


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

    # staff user can access management views
    def test_staff_can_access(self, client, staff_user, event: Event):
        client.force_login(staff_user)
        response = client.get(self.url)
        assert response.status_code == 200


class TestEventCreateView:
    url = reverse('events:event_create')

    # regular user gets 403
    def test_requires_editor_permission(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # editor starts with no visible ticket tier rows; JavaScript uses the template for new rows
    def test_ticket_tier_editor_starts_without_blank_row(self, client, editor):
        client.force_login(editor)

        response = client.get(self.url)

        assert response.status_code == 200
        assert response.context['ticket_formset'].total_form_count() == 0
        assert 'data-manage-formset-empty-form' in response.content.decode()

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
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        response = client.post(self.url, data)
        event = Event.objects.get(slug='new-event')
        assert response.status_code == 302
        assert response['Location'] == reverse('events:event_edit', kwargs={'pk': event.pk})
        assert set(event.tags.names()) == {'meetup', 'social'}
        messages = list(get_messages(response.wsgi_request))
        assert any('created' in str(m) for m in messages)

    # editor can create ticket tiers while creating an event
    def test_creates_ticket_tiers(self, client, editor):
        client.force_login(editor)
        data = {
            'title': 'New Event',
            'slug': 'new-event',
            'description': 'Event description.',
            'location': 'Wellington',
            'start': '2026-06-15',
            'publish_status': AVAILABLE,
            'tags': '',
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '1',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '25.00',
            'ticket_tiers-0-currency': 'AUD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '0',
        }
        response = client.post(self.url, data)
        event = Event.objects.get(slug='new-event')
        tier = event.ticket_tiers.get()
        assert response.status_code == 302
        assert tier.name == 'Standard'
        assert tier.price == Decimal('25.00')
        assert tier.currency == 'AUD'

    # geocoding task is enqueued when address is provided
    @patch('apps.events.views.manage.transaction.on_commit', lambda fn: fn())
    @patch('apps.events.views.manage.geocode_event')
    def test_geocoding_on_create(self, mock_task, client, editor):
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
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        client.post(self.url, data)
        event = Event.objects.get(slug='geocode-test')
        mock_task.assert_called_once_with(event.pk, '123 Main St, Wellington')


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
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        event.refresh_from_db()
        assert event.title == 'Updated Title'
        assert list(event.tags.names()) == ['edited']
        messages = list(get_messages(response.wsgi_request))
        assert any('saved' in str(m) for m in messages)

    # ticket tier editor exposes visible controls for manual ordering
    def test_ticket_tier_editor_renders_order_controls(self, client, editor, event: Event):
        EventTicketTier.objects.create(event=event, name='Standard', price=Decimal('20.00'), currency='NZD')
        client.force_login(editor)

        response = client.get(reverse('events:event_edit', kwargs={'pk': event.pk}))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-manage-formset data-manage-formset-orderable' in content
        assert 'manage-formset-row-toolbar' in content
        assert 'class="manage-formset-drag-handle" data-manage-formset-drag-handle' in content
        assert 'manage-formset-row-body' in content
        assert 'Drag to reorder ticket tier' in content
        assert 'data-manage-formset-move-up' in content
        assert 'Move ticket tier up' in content
        assert 'data-manage-formset-move-down' in content
        assert 'Move ticket tier down' in content
        assert 'form-check-label' in content
        assert 'Sold out' in content

    # editor can update and add ticket tiers from the event form
    def test_updates_ticket_tiers(self, client, editor, event: Event):
        tier = EventTicketTier.objects.create(event=event, name='Standard', price=Decimal('20.00'), currency='NZD')
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '2',
            'ticket_tiers-INITIAL_FORMS': '1',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(tier.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '22.00',
            'ticket_tiers-0-currency': 'AUD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-is_sold_out': 'on',
            'ticket_tiers-0-order': '0',
            'ticket_tiers-1-name': 'Sponsor',
            'ticket_tiers-1-price': '10.00',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
            'ticket_tiers-1-order': '1',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        event.refresh_from_db()
        assert list(event.ticket_tiers.values_list('name', 'price', 'currency', 'is_sold_out')) == [
            ('Standard', Decimal('22.00'), 'AUD', True),
            ('Sponsor', Decimal('10.00'), 'NZD', False),
        ]

    # submitted order fields control the display order of saved ticket tiers
    def test_updates_ticket_tier_order(self, client, editor, event: Event):
        standard = EventTicketTier.objects.create(
            event=event, name='Standard', price=Decimal('20.00'), currency='NZD', order=0
        )
        sponsor = EventTicketTier.objects.create(
            event=event, name='Sponsor', price=Decimal('10.00'), currency='NZD', order=1
        )
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '2',
            'ticket_tiers-INITIAL_FORMS': '2',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(standard.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '20.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '1',
            'ticket_tiers-1-id': str(sponsor.pk),
            'ticket_tiers-1-name': 'Sponsor',
            'ticket_tiers-1-price': '10.00',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
            'ticket_tiers-1-order': '0',
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert list(event.ticket_tiers.values_list('name', 'order')) == [('Sponsor', 0), ('Standard', 1)]

    # missing order fields get sequential fallback values server-side
    def test_ticket_tier_blank_order_falls_back_to_sequence(self, client, editor, event: Event):
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '2',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '20.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '',
            'ticket_tiers-1-name': 'Sponsor',
            'ticket_tiers-1-price': '10.00',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert list(event.ticket_tiers.values_list('name', 'order')) == [('Standard', 0), ('Sponsor', 1)]

    # duplicate submitted order values are normalized to a stable contiguous sequence
    def test_ticket_tier_duplicate_order_values_are_normalized(self, client, editor, event: Event):
        standard = EventTicketTier.objects.create(
            event=event, name='Standard', price=Decimal('20.00'), currency='NZD', order=0
        )
        sponsor = EventTicketTier.objects.create(
            event=event, name='Sponsor', price=Decimal('10.00'), currency='NZD', order=1
        )
        vip = EventTicketTier.objects.create(event=event, name='VIP', price=Decimal('50.00'), currency='NZD', order=2)
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '3',
            'ticket_tiers-INITIAL_FORMS': '3',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(standard.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '20.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '0',
            'ticket_tiers-1-id': str(sponsor.pk),
            'ticket_tiers-1-name': 'Sponsor',
            'ticket_tiers-1-price': '10.00',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
            'ticket_tiers-1-order': '0',
            'ticket_tiers-2-id': str(vip.pk),
            'ticket_tiers-2-name': 'VIP',
            'ticket_tiers-2-price': '50.00',
            'ticket_tiers-2-currency': 'NZD',
            'ticket_tiers-2-available_from': '',
            'ticket_tiers-2-available_until': '',
            'ticket_tiers-2-order': '5',
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert list(event.ticket_tiers.values_list('name', 'order')) == [('Standard', 0), ('Sponsor', 1), ('VIP', 2)]

    # deleted ticket tiers are excluded when normalizing order values
    def test_ticket_tier_deleted_rows_are_excluded_from_order_normalization(self, client, editor, event: Event):
        standard = EventTicketTier.objects.create(
            event=event, name='Standard', price=Decimal('20.00'), currency='NZD', order=0
        )
        sponsor = EventTicketTier.objects.create(
            event=event, name='Sponsor', price=Decimal('10.00'), currency='NZD', order=1
        )
        vip = EventTicketTier.objects.create(event=event, name='VIP', price=Decimal('50.00'), currency='NZD', order=2)
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '3',
            'ticket_tiers-INITIAL_FORMS': '3',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(standard.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '20.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '0',
            'ticket_tiers-1-id': str(sponsor.pk),
            'ticket_tiers-1-name': 'Sponsor',
            'ticket_tiers-1-price': '10.00',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
            'ticket_tiers-1-order': '1',
            'ticket_tiers-1-DELETE': 'on',
            'ticket_tiers-2-id': str(vip.pk),
            'ticket_tiers-2-name': 'VIP',
            'ticket_tiers-2-price': '50.00',
            'ticket_tiers-2-currency': 'NZD',
            'ticket_tiers-2-available_from': '',
            'ticket_tiers-2-available_until': '',
            'ticket_tiers-2-order': '2',
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert list(event.ticket_tiers.values_list('name', 'order')) == [('Standard', 0), ('VIP', 1)]

    # blank extra tier rows do not block editing existing tiers
    def test_updates_ticket_tier_with_blank_extra_row(self, client, editor, event: Event):
        tier = EventTicketTier.objects.create(event=event, name='Standard', price=Decimal('20.00'), currency='NZD')
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '2',
            'ticket_tiers-INITIAL_FORMS': '1',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(tier.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '22.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '0',
            'ticket_tiers-1-name': '',
            'ticket_tiers-1-price': '',
            'ticket_tiers-1-currency': 'NZD',
            'ticket_tiers-1-available_from': '',
            'ticket_tiers-1-available_until': '',
            'ticket_tiers-1-order': '1',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        tier.refresh_from_db()
        assert tier.price == Decimal('22.00')
        assert event.ticket_tiers.count() == 1

    # editor can delete ticket tiers from the event form
    def test_deletes_ticket_tiers(self, client, editor, event: Event):
        tier = EventTicketTier.objects.create(event=event, name='Standard', price=Decimal('20.00'), currency='NZD')
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': event.title,
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '1',
            'ticket_tiers-INITIAL_FORMS': '1',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
            'ticket_tiers-0-id': str(tier.pk),
            'ticket_tiers-0-name': 'Standard',
            'ticket_tiers-0-price': '20.00',
            'ticket_tiers-0-currency': 'NZD',
            'ticket_tiers-0-available_from': '',
            'ticket_tiers-0-available_until': '',
            'ticket_tiers-0-order': '0',
            'ticket_tiers-0-DELETE': 'on',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert not EventTicketTier.objects.filter(pk=tier.pk).exists()

    # geocoding task is enqueued when address changes
    @patch('apps.events.views.manage.transaction.on_commit', lambda fn: fn())
    @patch('apps.events.views.manage.geocode_event')
    def test_geocoding_on_address_change(self, mock_task, client, editor, event: Event):
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
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        client.post(url, data)
        mock_task.assert_called_once_with(event.pk, 'New Address, Wellington')

    # clearing address clears lat/lng without enqueuing geocoding
    @patch('apps.events.views.manage.geocode_event')
    def test_clearing_address_clears_coords(self, mock_task, client, editor, event: Event):
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
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        client.post(url, data)
        event.refresh_from_db()
        assert event.latitude is None
        assert event.longitude is None
        mock_task.assert_not_called()

    # updating event without changing address does not enqueue geocoding
    @patch('apps.events.views.manage.geocode_event')
    def test_address_unchanged_skips_geocoding(self, mock_task, client, editor, event: Event):
        event.address = '123 Main St'
        event.save()
        client.force_login(editor)
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        data = {
            'title': 'Updated Title',
            'slug': event.slug,
            'description': event.description,
            'location': event.location,
            'address': '123 Main St',
            'start': event.start.isoformat(),
            'publish_status': event.publish_status,
            'tags': ', '.join(event.tags.names()),
            'image_ppoi': '0.5x0.5',
            'ticket_tiers-TOTAL_FORMS': '0',
            'ticket_tiers-INITIAL_FORMS': '0',
            'ticket_tiers-MIN_NUM_FORMS': '0',
            'ticket_tiers-MAX_NUM_FORMS': '1000',
        }
        client.post(url, data)
        mock_task.assert_not_called()


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
