import factory
from factory import Faker
from factory.django import DjangoModelFactory

from apps.core.tests.factories import TaggedModelFactory

from ..models import Event


class EventFactory(TaggedModelFactory):
    title = Faker('name')

    description = Faker('paragraph')
    location = Faker('sentence')
    url = Faker('url')

    start = Faker('future_date')

    class Meta:
        model = Event
        skip_postgeneration_save = True


class PastEventFactory(EventFactory):
    start = Faker('past_date')


class EventInterestFactory(DjangoModelFactory):
    class Meta:
        model = 'events.EventInterest'

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory('apps.accounts.tests.factories.UserFactory')
    status = 'interested'
