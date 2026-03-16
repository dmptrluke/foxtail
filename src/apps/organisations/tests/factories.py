from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from ..models import EventSeries, Organisation, SocialLink


class OrganisationFactory(DjangoModelFactory):
    name = Faker('company')
    description = Faker('paragraph')
    url = Faker('url')
    group_type = 'organisation'
    region = ''

    class Meta:
        model = Organisation


class SocialLinkFactory(DjangoModelFactory):
    organisation = SubFactory(OrganisationFactory)
    platform = 'discord'
    url = Faker('url')

    class Meta:
        model = SocialLink


class EventSeriesFactory(DjangoModelFactory):
    name = Faker('catch_phrase')
    description = Faker('paragraph')
    organisation = SubFactory(OrganisationFactory)

    class Meta:
        model = EventSeries
