from datetime import date
from types import SimpleNamespace

from ..templatetags.event_calendar import event_calendar


class TestEventCalendar:
    def _make_event(self, start, end=None):
        return SimpleNamespace(start=start, end=end)

    # single-day event shows 7 days (3 pad + 1 event + 3 pad)
    def test_single_day_event(self):
        event = self._make_event(date(2026, 6, 15))
        html = event_calendar(event)
        assert 'active first last' in html
        assert 'June 2026' in html

    # multi-day event (2 days) highlights both days
    def test_two_day_event(self):
        event = self._make_event(date(2026, 6, 15), date(2026, 6, 16))
        html = event_calendar(event)
        assert 'active first' in html
        assert 'active last' in html

    # long event (>5 days) uses 1-day padding
    def test_long_event_padding(self):
        event = self._make_event(date(2026, 6, 10), date(2026, 6, 20))
        html = event_calendar(event)
        day_count = html.count('event-cal-day')
        assert day_count == 13  # 1 pad + 11 event days + 1 pad

    # medium event (4-5 days) uses 2-day padding
    def test_medium_event_padding(self):
        event = self._make_event(date(2026, 6, 10), date(2026, 6, 14))
        html = event_calendar(event)
        day_count = html.count('event-cal-day')
        assert day_count == 9  # 2 pad + 5 event days + 2 pad

    # cross-month event shows abbreviated month range
    def test_cross_month_label(self):
        event = self._make_event(date(2026, 6, 28), date(2026, 7, 2))
        html = event_calendar(event)
        assert 'Jun' in html
        assert 'Jul 2026' in html

    # day numbers render correctly
    def test_day_numbers(self):
        event = self._make_event(date(2026, 6, 15))
        html = event_calendar(event)
        assert '>15<' in html

    # non-active days don't have active class
    def test_non_active_days(self):
        event = self._make_event(date(2026, 6, 15))
        html = event_calendar(event)
        assert 'event-cal-day">' in html  # non-active day has no extra classes
