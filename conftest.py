from django.test import RequestFactory

import pytest
from pytest_factoryboy import register
from selenium import webdriver

from apps.accounts.tests.factories import UserFactory, UserNoPasswordFactory
from apps.content.tests.factories import PageFactory
from apps.events.tests.factories import EventFactory
from foxtail_blog.tests.factories import PostFactory

# accounts
register(UserFactory, "user")
register(UserFactory, "second_user")
register(UserFactory, "third_user")
register(UserNoPasswordFactory, "user_without_password")

# blog
register(PostFactory, "post")
register(PostFactory, "second_post")

# content
register(PageFactory)

# events
register(EventFactory)


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture(scope='module')
def driver(request):
    """Provide a selenium webdriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(options=options)

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
