from factory import DjangoModelFactory, Faker

from ..models import Event


class EventFactory(DjangoModelFactory):
    title = Faker('name')
    tags = f"{Faker('words')}, {Faker('words')}"

    description = Faker('paragraph')
    location = Faker('sentence')
    url = Faker('url')

    start = Faker('future_date')

    class Meta:
        model = Event
