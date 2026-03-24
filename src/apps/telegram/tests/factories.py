import secrets
from datetime import timedelta

from django.utils.timezone import now

import factory
from factory.django import DjangoModelFactory

from apps.accounts.tests.factories import UserFactory
from apps.telegram.models import LinkToken, TelegramLink


class TelegramLinkFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    telegram_id = factory.LazyFunction(lambda: secrets.randbelow(10**10) + 10**8)
    username = factory.Faker('user_name')
    name = factory.Faker('name')

    class Meta:
        model = TelegramLink


class LinkTokenFactory(DjangoModelFactory):
    telegram_id = factory.LazyFunction(lambda: secrets.randbelow(10**10) + 10**8)
    username = factory.Faker('user_name')
    token = factory.LazyFunction(lambda: secrets.token_urlsafe(48))
    expires_at = factory.LazyFunction(lambda: now() + timedelta(minutes=15))

    class Meta:
        model = LinkToken


class ExpiredLinkTokenFactory(LinkTokenFactory):
    expires_at = factory.LazyFunction(lambda: now() - timedelta(minutes=1))
