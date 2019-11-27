import pytest
import os
from django.core.management import call_command
from selenium import webdriver


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/data.json')


@pytest.fixture(scope='module')
def driver(request):
    """Provide a selenium webdriver instance."""
    driver = os.environ.get('ChromeWebDriver', None)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    if driver:
        browser = webdriver.Chrome(driver, options=options)
    else:
        browser = webdriver.Chrome(options=options)

    yield browser

    # TearDown
    browser.quit()
