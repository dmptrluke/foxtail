from datetime import UTC

import factory
from factory import Faker
from factory.django import DjangoModelFactory
from published.constants import AVAILABLE

from apps.accounts.tests.factories import UserFactory
from apps.core.tests.factories import TaggedModelFactory

from ..models import Author, Comment, Post


class AuthorFactory(DjangoModelFactory):
    name = Faker('name')

    class Meta:
        model = Author


class PostFactory(TaggedModelFactory):
    title = Faker('name')
    slug = Faker('slug')

    allow_comments = True
    publish_status = AVAILABLE

    author = factory.SubFactory(AuthorFactory)
    created = Faker('date_time_this_year', tzinfo=UTC)

    text = Faker('paragraph')

    class Meta:
        model = Post
        skip_postgeneration_save = True


class CommentFactory(DjangoModelFactory):
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)

    text = Faker('paragraph')

    class Meta:
        model = Comment
