import pytest
from django.core.management import call_command
from selenium import webdriver


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/data.json')


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
