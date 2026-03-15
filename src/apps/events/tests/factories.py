import factory
from factory import Faker
from factory.django import DjangoModelFactory
from faker import Faker as FakerLib

from ..models import Event

fake = FakerLib()


class EventFactory(DjangoModelFactory):
    title = Faker('name')

    description = Faker('paragraph')
    location = Faker('sentence')
    url = Faker('url')

    start = Faker('future_date')

    class Meta:
        model = Event
        skip_postgeneration_save = True

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)
        else:
            self.tags.add(fake.word(), fake.word())


class PastEventFactory(EventFactory):
    start = Faker('past_date')


class EventInterestFactory(DjangoModelFactory):
    class Meta:
        model = 'events.EventInterest'

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory('apps.accounts.tests.factories.UserFactory')
    status = 'interested'
