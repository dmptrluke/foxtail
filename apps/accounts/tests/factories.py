from typing import Any, Sequence

from django.contrib.auth import get_user_model

from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from faker import Faker as StockFaker


class UserNoPasswordFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    date_of_birth = Faker("date_between", start_date="-50y", end_date="-18y")
    full_name = Faker("name")
    password = "!NONE"

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]


class UserFactory(UserNoPasswordFactory):
    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = StockFaker().password(
            length=42,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
        self.set_password(password)
