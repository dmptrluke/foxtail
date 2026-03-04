from django.urls import reverse

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_account_creation(driver, live_server, settings):
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_NAME = 'csrftoken'
    settings.SESSION_COOKIE_NAME = 'sessionid'

    proto_user = UserFactory.build()

    # user visits the website
    driver.get(live_server.url)

    # user sees the create account button, and clicks it
    create_account_btn = driver.find_element(By.LINK_TEXT, "Create Account")
    assert create_account_btn

    create_account_btn.click()

    # we are now on the account creation page
    WebDriverWait(driver, 10).until(EC.url_contains('/accounts/signup/'))
    assert 'Create Account' in driver.title

    # wait for the form to be fully loaded with CSRF token
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="csrfmiddlewaretoken"]'))
    )

    # the user enters their details
    username_field = driver.find_element(By.NAME, 'username')
    username_field.send_keys(proto_user.username)

    email_field = driver.find_element(By.NAME, 'email')
    email_field.send_keys(proto_user.email)

    password1_field = driver.find_element(By.NAME, 'password1')
    password1_field.send_keys(proto_user._password)

    password2_field = driver.find_element(By.NAME, 'password2')
    password2_field.send_keys(proto_user._password)

    # and hits submit, creating their account
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "create_account_submit"))
    )
    submit_btn.click()

    # we should now be back at the homepage
    WebDriverWait(driver, 10).until(EC.url_to_be(live_server.url + reverse('content:index')))

    # the user sees a green alert
    alert = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )
    assert f"Successfully signed in as {proto_user.username}" in alert.text
