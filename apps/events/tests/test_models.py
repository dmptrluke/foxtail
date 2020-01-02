import pytest

from ..models import Event

pytestmark = pytest.mark.django_db


def test_string_representation(event: Event):
    assert str(event) == event.title


def test_get_absolute_url(event: Event):
    assert event.get_absolute_url() == f"/events/{event.start.year}/{event.slug}/"
