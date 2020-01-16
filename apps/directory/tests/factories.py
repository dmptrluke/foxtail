from factory import DjangoModelFactory, Faker, SubFactory

from apps.accounts.tests.factories import UserFactory

from ..models import Profile


class ProfileFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    profile_URL = Faker('slug')

    class Meta:
        model = Profile
        django_get_or_create = ["user"]
