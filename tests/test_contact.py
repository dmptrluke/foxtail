from django.core import mail
from django.urls import reverse

import pytest
from faker import Faker

fake = Faker()
pytestmark = pytest.mark.django_db


def test_unauthenticated_user_contact(driver, live_server, settings):
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_NAME = 'csrftoken'
    settings.SESSION_COOKIE_NAME = 'sessionid'

    # user heads to the contact page
    driver.get(live_server.url + reverse('contact:contact'))

    # the title contains contact
    assert 'contact' in driver.title.lower()

    # we generate some data, now
    name = fake.name()
    email = fake.email()
    message = fake.paragraphs()

    # the user fills out the form
    name_field = driver.find_element_by_name('name')
    name_field.send_keys(name)

    email_field = driver.find_element_by_name('email')
    email_field.send_keys(email)

    message_field = driver.find_element_by_name('message')
    message_field.send_keys('\n\n'.join(message))

    driver.find_element_by_id("contact_submit").click()

    driver.implicitly_wait(1)

    # we should still be a the same page
    assert driver.current_url == live_server.url + reverse('contact:contact')

    # the user sees a green alert
    alert = driver.find_element_by_class_name('alert-success')
    assert "Your message has been sent" in alert.text

    # we have an email sent!
    assert len(mail.outbox) == 1

    # and it has all the right info
    assert name in mail.outbox[0].body
    assert email in mail.outbox[0].body
    for paragraph in message:
        assert paragraph in mail.outbox[0].body
