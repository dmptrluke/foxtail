from factory import DjangoModelFactory, Faker

from ..models import Page


class PageFactory(DjangoModelFactory):
    title = Faker('name')
    slug = Faker('slug')

    subtitle = Faker('sentence')

    body = Faker('paragraph')

    class Meta:
        model = Page
