import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from selenium import webdriver


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/data.json')


@pytest.fixture()
def user(db):
    """Add a test user to the database."""
    user_ = get_user_model().objects.create(
        username='test',
        email='test@example.com'
    )

    return user_


@pytest.fixture(scope='module')
def driver(request):
    """Provide a selenium webdriver instance."""
    # SetUp
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    browser = webdriver.Chrome(options=options)

    yield browser

    # TearDown
    browser.quit()


@pytest.fixture()
def authenticated_driver(driver, client, live_server, user, settings):
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
