from django.test import RequestFactory

import pytest
from published.constants import NEVER_AVAILABLE
from pytest_factoryboy import register
from selenium import webdriver

from apps.accounts.tests.factories import UserFactory, UserNoPasswordFactory
from apps.blog.tests.factories import AuthorFactory, CommentFactory, PostFactory
from apps.content.tests.factories import PageFactory
from apps.directory.tests.factories import ProfileFactory
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

# directory
register(ProfileFactory)

# events
register(EventFactory)
register(PastEventFactory, 'past_event')


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def driver(request):
    """Provide a selenium webdriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    browser = webdriver.Chrome(options=options)

    # Make the fixed navbar static so it doesn't intercept Selenium clicks
    browser.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {
            'source': 'document.addEventListener("DOMContentLoaded",'
            '() => document.querySelectorAll(".fixed-top")'
            '.forEach(el => el.style.setProperty("position", "static", "important")));'
        },
    )

    yield browser

    browser.quit()


@pytest.fixture
def authenticated_driver(db, driver, client, live_server, user, settings):
    """Return a browser instance with logged-in user session."""
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_NAME = 'csrftoken'
    settings.SESSION_COOKIE_NAME = 'sessionid'

    client.force_login(user)
    cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    driver.get(live_server.url)
    driver.add_cookie({'name': settings.SESSION_COOKIE_NAME, 'value': cookie.value, 'secure': False, 'path': '/'})
    driver.refresh()

    return driver
