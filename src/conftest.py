from django.test import RequestFactory

import pytest
from published.constants import NEVER_AVAILABLE
from pytest_factoryboy import register

from apps.accounts.tests.factories import UserFactory, UserNoPasswordFactory
from apps.blog.tests.factories import AuthorFactory, CommentFactory, PostFactory
from apps.content.tests.factories import PageFactory
from apps.events.tests.factories import EventFactory, PastEventFactory

# accounts
register(UserFactory, 'user')
register(UserFactory, 'second_user')
register(UserFactory, 'third_user')
register(UserNoPasswordFactory, 'user_without_password')

# blog
register(AuthorFactory)
register(PostFactory, 'post')
register(PostFactory, 'second_post')
register(PostFactory, 'hidden_post', publish_status=NEVER_AVAILABLE)
register(CommentFactory, 'comment')

# content
register(PageFactory)

# events
register(EventFactory)
register(PastEventFactory, 'past_event')


@pytest.fixture(autouse=True)
def _disable_rate_limits(request, settings):
    if 'keep_rate_limits' not in request.keywords:
        settings.ACCOUNT_RATE_LIMITS = {}


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
