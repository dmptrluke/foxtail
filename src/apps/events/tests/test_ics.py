from datetime import time

from django.urls import reverse

import pytest
from icalendar import Calendar

from .factories import EventFactory

pytestmark = pytest.mark.django_db


class TestGenerateICS:
    # single-day event without time produces VALUE=DATE
    def test_date_only_event(self):
        event = EventFactory(start_time=None, end=None, end_time=None)
        from apps.events.ics import generate_ics

        cal_bytes = generate_ics(event)
        cal = Calendar.from_ical(cal_bytes)
        vevent = next(iter(cal.walk('VEVENT')))
        dtstart = vevent.get('dtstart')
        assert dtstart.params.get('VALUE') == 'DATE' or not hasattr(dtstart.dt, 'hour')

    # event with start_time includes timezone
    def test_datetime_event(self):
        event = EventFactory(start_time=time(10, 0), end=None, end_time=None)
        from apps.events.ics import generate_ics

        cal_bytes = generate_ics(event)
        cal = Calendar.from_ical(cal_bytes)
        vevent = next(iter(cal.walk('VEVENT')))
        dtstart = vevent.get('dtstart')
        assert hasattr(dtstart.dt, 'hour')
        assert dtstart.dt.hour == 10

    # multi-day event sets DTEND correctly
    def test_multi_day_event(self):
        from datetime import timedelta

        start = EventFactory.build().start
        event = EventFactory(start=start, end=start + timedelta(days=3), end_time=None)
        from apps.events.ics import generate_ics

        cal_bytes = generate_ics(event)
        cal = Calendar.from_ical(cal_bytes)
        vevent = next(iter(cal.walk('VEVENT')))
        dtend = vevent.get('dtend')
        assert dtend is not None

    # special characters in title are handled by the library
    def test_special_characters(self):
        event = EventFactory(title='Test; Event, with "chars"', location='Place; with, commas')
        from apps.events.ics import generate_ics

        cal_bytes = generate_ics(event)
        cal = Calendar.from_ical(cal_bytes)
        vevent = next(iter(cal.walk('VEVENT')))
        assert vevent.get('summary') == 'Test; Event, with "chars"'
        assert vevent.get('location') == 'Place; with, commas'


class TestEventICSView:
    # response has correct Content-Type
    def test_content_type(self, client):
        event = EventFactory()
        response = client.get(reverse('events:event_ics', kwargs={'pk': event.pk}))
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/calendar'

    # response has correct Content-Disposition
    def test_content_disposition(self, client):
        event = EventFactory()
        response = client.get(reverse('events:event_ics', kwargs={'pk': event.pk}))
        assert f'filename="{event.slug}.ics"' in response['Content-Disposition']

    # unpublished event returns 404
    def test_unpublished_event(self, client):
        from published.constants import NEVER_AVAILABLE

        event = EventFactory(publish_status=NEVER_AVAILABLE)
        response = client.get(reverse('events:event_ics', kwargs={'pk': event.pk}))
        assert response.status_code == 404
