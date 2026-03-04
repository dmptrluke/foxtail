from django.test import RequestFactory

import pytest

from ..models import Event
from ..views import EventDetail, EventList

pytestmark = pytest.mark.django_db


def test_list(event: Event, past_event: Event, request_factory: RequestFactory):
    view = EventList()
    request = request_factory.get('/events/')

    view.setup(request)

    view.object_list = view.get_queryset()
    context = view.get_context_data()

    # future event should be in upcoming
    assert len(context['upcoming_events']) == 1
    assert context['upcoming_events'][0].title == event.title

    # past event should be in past
    assert len(context['past_events']) == 1
    assert context['past_events'][0].title == past_event.title


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
