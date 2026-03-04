from django.test import RequestFactory

import pytest

from ..models import Event
from ..views import EventDetail, EventList

pytestmark = pytest.mark.django_db


def test_list(event: Event, request_factory: RequestFactory):
    view = EventList()
    request = request_factory.get('/events/')

    view.setup(request)

    view.object_list = view.get_queryset()
    context = view.get_context_data()

    # there should be one event
    assert len(context['event_list']) == 1

    # the event should be correct
    event_context: Event = context['event_list'][0]
    assert event_context.title == event.title


def test_detail(event: Event, request_factory: RequestFactory):
    view = EventDetail()
    request = request_factory.get(f'/events/{event.start.year}/{event.slug}/')

    view.object = event
    view.setup(request)

    context = view.get_context_data()

    # the event should be correct
    event_context: Event = context['event']
    assert event_context.title == event.title
    assert event_context.description == event.description
