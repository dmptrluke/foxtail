from django.contrib.auth import get_user_model

import factory
from factory import Faker, Iterator
from factory.django import DjangoModelFactory
from published.constants import AVAILABLE

from ..models import Author, Comment, Post


class AuthorFactory(DjangoModelFactory):
    name = Faker('name')

    class Meta:
        model = Author


class PostFactory(DjangoModelFactory):
    title = Faker('name')
    slug = Faker('slug')

    tags = f'{Faker("words")}, {Faker("words")}'

    allow_comments = True
    publish_status = AVAILABLE

    author = factory.SubFactory(AuthorFactory)
    created = Faker('date_time_this_year')

    text = Faker('paragraph')

    class Meta:
        model = Post


class CommentFactory(DjangoModelFactory):
    post = Iterator(Post.objects.all())
    author = Iterator(get_user_model().objects.all())

    text = Faker('paragraph')
    created = Faker('date_time_this_year')

    class Meta:
        model = Comment
