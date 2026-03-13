from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from ..models import EventSeries, Organisation


class OrganisationFactory(DjangoModelFactory):
    name = Faker('company')
    description = Faker('paragraph')
    url = Faker('url')

    class Meta:
        model = Organisation


class EventSeriesFactory(DjangoModelFactory):
    name = Faker('catch_phrase')
    description = Faker('paragraph')
    organisation = SubFactory(OrganisationFactory)

    class Meta:
        model = EventSeries
