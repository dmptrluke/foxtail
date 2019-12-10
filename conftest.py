import pytest
from django.core.management import call_command
from selenium import webdriver


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/data.json')


@pytest.fixture
def user(db, django_user_model, django_username_field):
    """A Django user.
    This uses an existing user with username "user", or creates a new one with
    password "password".
    """
    user_model = django_user_model
    username_field = django_username_field
    username = "user@example.com" if username_field == "email" else "test"

    try:
        user = user_model._default_manager.get(**{username_field: username})
    except user_model.DoesNotExist:
        extra_fields = {}
        if username_field not in ("username", "email"):
            extra_fields[username_field] = "test"
        user = user_model._default_manager.create_user(
            username, "user@example.com", "password", **extra_fields
        )
    return user


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
