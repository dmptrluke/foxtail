from datetime import UTC

import factory
from factory import Faker
from factory.django import DjangoModelFactory
from faker import Faker as FakerLib
from published.constants import AVAILABLE

from apps.accounts.tests.factories import UserFactory

from ..models import Author, Comment, Post

fake = FakerLib()


class AuthorFactory(DjangoModelFactory):
    name = Faker('name')

    class Meta:
        model = Author


class PostFactory(DjangoModelFactory):
    title = Faker('name')
    slug = Faker('slug')

    allow_comments = True
    publish_status = AVAILABLE

    author = factory.SubFactory(AuthorFactory)
    created = Faker('date_time_this_year', tzinfo=UTC)

    text = Faker('paragraph')

    class Meta:
        model = Post

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)
        else:
            self.tags.add(fake.word(), fake.word())


class CommentFactory(DjangoModelFactory):
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)

    text = Faker('paragraph')

    class Meta:
        model = Comment
