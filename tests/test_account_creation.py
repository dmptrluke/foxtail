import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_account_creation(driver, live_server, settings):
    settings.RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    settings.RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_NAME = 'csrftoken'
    settings.SESSION_COOKIE_NAME = 'sessionid'

    # user visits the website
    driver.get(live_server.url)

    # user sees the create account button, and clicks it
    create_account_btn = driver.find_element_by_link_text("Create Account")
    assert create_account_btn

    create_account_btn.click()

    # we are now on the account creation page
    assert reverse('account_signup') in driver.current_url

    # the page title is now for create account page
    assert 'Create Account' in driver.title

    # the user enters their details
    username_field = driver.find_element_by_name('username')
    username_field.send_keys('John Doe')

    email_field = driver.find_element_by_name('email')
    email_field.send_keys('test@example.com')

    password1_field = driver.find_element_by_name('password1')
    password1_field.send_keys('ValidPassword24*')

    password2_field = driver.find_element_by_name('password2')
    password2_field.send_keys('ValidPassword24*')

    driver.find_element_by_id("create_account_submit").click()
