from django.urls import reverse

import pytest

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
    create_account_btn = driver.find_element_by_link_text("Create Account")
    assert create_account_btn

    create_account_btn.click()

    # we are now on the account creation page
    assert driver.current_url == live_server.url + reverse('account_signup')

    # the page title is now for create account page
    assert 'Create Account' in driver.title

    # the user enters their details
    username_field = driver.find_element_by_name('username')
    username_field.send_keys(proto_user.username)

    email_field = driver.find_element_by_name('email')
    email_field.send_keys(proto_user.email)

    password1_field = driver.find_element_by_name('password1')
    password1_field.send_keys(proto_user._password)

    password2_field = driver.find_element_by_name('password2')
    password2_field.send_keys(proto_user._password)

    # and hits submit, creating their account
    driver.find_element_by_id("create_account_submit").click()

    # we should now be back at the homepage
    assert driver.current_url == live_server.url + reverse('content:index')

    # the user sees a green alert
    alert = driver.find_element_by_class_name('alert-success')
    assert f"Successfully signed in as {proto_user.username}" in alert.text
