from django.test import RequestFactory

import pytest
from published.constants import NEVER_AVAILABLE
from pytest_factoryboy import register

from apps.accounts.tests.factories import UserFactory, UserNoPasswordFactory
from apps.blog.tests.factories import AuthorFactory, CommentFactory, PostFactory
from apps.content.tests.factories import PageFactory
from apps.events.tests.factories import EventFactory, EventInterestFactory, PastEventFactory
from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory, SocialLinkFactory

# accounts
register(UserFactory, 'user')
register(UserFactory, 'second_user')
register(UserFactory, 'third_user')
register(UserFactory, 'fourth_user')
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
register(EventInterestFactory)

# organisations
register(OrganisationFactory)
register(SocialLinkFactory)
register(EventSeriesFactory)


@pytest.fixture(autouse=True)
def _testing_overrides(request, settings):
    # simplified staticfiles (no manifest needed)
    settings.STORAGES = {
        **settings.STORAGES,
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
    settings.WHITENOISE_AUTOREFRESH = True
    # disable debug toolbar in tests (middleware bombs when URL conf isn't fully wired)
    settings.DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda _: False}
    if 'keep_rate_limits' not in request.keywords:
        settings.ACCOUNT_RATE_LIMITS = {}


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
