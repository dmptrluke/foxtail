from datetime import timedelta

from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()


@register.simple_tag
def event_calendar(event):
    """Render a mini calendar strip centered around the event dates.

    Shows ~9 days with event days highlighted.
    """
    start = event.start
    end = event.end or start
    event_days = {start + timedelta(days=i) for i in range((end - start).days + 1)}

    # Show a window of days around the event
    total_event_days = len(event_days)
    if total_event_days <= 3:
        pad_before = 3
        pad_after = 3
    elif total_event_days <= 5:
        pad_before = 2
        pad_after = 2
    else:
        pad_before = 1
        pad_after = 1

    first_day = start - timedelta(days=pad_before)
    last_day = end + timedelta(days=pad_after)
    total_days = (last_day - first_day).days + 1

    days_html = []
    for i in range(total_days):
        day = first_day + timedelta(days=i)
        is_active = day in event_days
        is_first = day == start
        is_last = day == end

        cls = 'event-cal-day'
        if is_active:
            cls += ' active'
        if is_first:
            cls += ' first'
        if is_last:
            cls += ' last'

        days_html.append(
            format_html(
                '<div class="{cls}">'
                '<span class="event-cal-name">{name}</span>'
                '<span class="event-cal-num">{num}</span>'
                '</div>',
                cls=cls,
                name=day.strftime('%a'),
                num=day.day,
            )
        )

    inner = format_html_join('', '{}', [(d,) for d in days_html])

    # Month label(s)
    if start.month == end.month:
        month_label = start.strftime('%B %Y')
    else:
        month_label = f'{start.strftime("%b")} - {end.strftime("%b %Y")}'

    return format_html(
        '<div class="event-cal">'
        '<div class="event-cal-label">{label}</div>'
        '<div class="event-cal-strip">{days}</div>'
        '</div>',
        label=month_label,
        days=inner,
    )
