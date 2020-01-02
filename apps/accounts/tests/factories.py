from typing import Any, Sequence

from django.contrib.auth import get_user_model

from factory import DjangoModelFactory, Faker, post_generation


class UserNoPasswordFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    full_name = Faker("name")
    password = "!NONE"

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]


class UserFactory(UserNoPasswordFactory):
    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = Faker(
            "password",
            length=42,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        ).generate(extra_kwargs={})
        self.set_password(password)
