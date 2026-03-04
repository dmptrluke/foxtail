from datetime import date, time

import pytest
from pytz import utc

from ..models import Event

pytestmark = pytest.mark.django_db


class TestEvent:
    def test_string_representation(self, event: Event):
        assert str(event) == event.title

    def test_get_absolute_url(self, event: Event):
        assert event.get_absolute_url() == f"/events/{event.start.year}/{event.slug}/"

    def test_is_ended(self, event: Event):
        event.end = date(2019, 12, 2)

        assert event.is_ended

    def test_is_ended_with_time(self, event: Event):
        event.end = date(2019, 12, 2)
        event.end_time = time(12, 30, 00, tzinfo=utc)

        assert event.is_ended
