from factory import Faker
from factory.django import DjangoModelFactory

from ..models import Page


class PageFactory(DjangoModelFactory):
    title = Faker('name')
    slug = Faker('slug')

    subtitle = Faker('sentence')

    body = Faker('paragraph')

    class Meta:
        model = Page
