from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils.html import strip_tags

from icalendar import Calendar
from icalendar import Event as IcsEvent

NZ_TZ = ZoneInfo('Pacific/Auckland')


def generate_ics(event):
    """Generate RFC 5545 compliant ICS calendar data for an event"""
    cal = Calendar()
    cal.add('prodid', f'-//{settings.SITE_DOMAIN}//events//EN')
    cal.add('version', '2.0')

    ics_event = IcsEvent()
    ics_event.add('uid', f'event-{event.pk}@{settings.SITE_DOMAIN}')
    ics_event.add('summary', event.title)

    if event.start_time:
        ics_event.add('dtstart', datetime.combine(event.start, event.start_time, tzinfo=NZ_TZ))
    else:
        ics_event.add('dtstart', event.start)

    if event.end:
        if event.end_time:
            ics_event.add('dtend', datetime.combine(event.end, event.end_time, tzinfo=NZ_TZ))
        else:
            ics_event.add('dtend', event.end + timedelta(days=1))
    elif event.end_time:
        ics_event.add('dtend', datetime.combine(event.start, event.end_time, tzinfo=NZ_TZ))

    if event.location:
        ics_event.add('location', event.location)
    if event.description_rendered:
        ics_event.add('description', strip_tags(event.description_rendered))
    ics_event.add('url', f'{settings.SITE_URL}{event.get_absolute_url()}')

    cal.add_component(ics_event)
    return cal.to_ical()
