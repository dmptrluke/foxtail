from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core import signing
from django.urls import reverse

import pytest
from formguard.test import GuardedFormTestMixin, make_guard_token

from conftest import CAPTCHA_FIELD

pytestmark = pytest.mark.django_db


class TestContactView(GuardedFormTestMixin):
    url = reverse('contact:contact')

    # successful submission sends email with correct subject, recipients, and body
    def test_submission_sends_email(self, client, mailoutbox, settings):
        data = {
            'name': 'Fox McCloud',
            'email': 'fox@example.com',
            'message': 'Hello there',
            **self.guard_data(),
            **CAPTCHA_FIELD,
        }
        response = client.post(self.url, data)

        assert response.status_code == 302
        assert len(mailoutbox) == 1
        email = mailoutbox[0]
        assert email.subject == 'Contact form submission - Fox McCloud'
        assert email.to == settings.CONTACT_EMAILS
        assert 'Fox McCloud' in email.body
        assert 'fox@example.com' in email.body
        assert 'Hello there' in email.body
        messages = list(get_messages(response.wsgi_request))
        assert any('Your message has been sent' in str(m) for m in messages)

    # authenticated user's username is included in email context
    def test_authenticated_user_included_in_email(self, client, user, mailoutbox):
        client.force_login(user)
        data = {
            'name': 'Fox',
            'email': 'fox@example.com',
            'message': 'Hello',
            **self.guard_data(),
            **CAPTCHA_FIELD,
        }
        client.post(self.url, data)

        assert len(mailoutbox) == 1
        assert user.username in mailoutbox[0].body

    # honeypot field filled in blocks submission silently
    def test_honeypot_field_blocks_submission(self, client, mailoutbox, caplog):
        data = {
            'name': 'Bot',
            'email': 'bot@spam.com',
            'message': 'Buy now',
            'website': 'http://spam.com',
            'fg_token': make_guard_token(),
            **CAPTCHA_FIELD,
        }
        response = client.post(self.url, data)

        assert response.status_code == 302
        assert len(mailoutbox) == 0
        assert 'formguard triggered' in caplog.text
        messages = list(get_messages(response.wsgi_request))
        assert any('Your message has been sent' in str(m) for m in messages)

    # submission faster than minimum time blocks silently
    def test_honeypot_timer_blocks_fast_submission(self, client, mailoutbox, caplog):
        now = 1000.0
        recent_timestamp = signing.dumps(now, salt='formguard')
        data = {
            'name': 'Bot',
            'email': 'bot@spam.com',
            'message': 'Buy now',
            'fg_token': recent_timestamp,
            **CAPTCHA_FIELD,
        }
        with patch('formguard.checks.time.time', return_value=now + 1):
            response = client.post(self.url, data)

        assert response.status_code == 302
        assert len(mailoutbox) == 0
        assert 'formguard triggered' in caplog.text

    # tampered or missing timestamp blocks silently
    def test_honeypot_bad_signature_blocks_submission(self, client, mailoutbox, caplog):
        data = {
            'name': 'Bot',
            'email': 'bot@spam.com',
            'message': 'Buy now',
            'fg_token': 'tampered-garbage',
            **CAPTCHA_FIELD,
        }
        response = client.post(self.url, data)

        assert response.status_code == 302
        assert len(mailoutbox) == 0
        assert 'formguard triggered' in caplog.text

    # GET with ?email= query param pre-fills the email field
    def test_email_prefill_from_query_param(self, client):
        response = client.get(self.url, {'email': 'prefilled@example.com'})

        form = response.context['form']
        assert form.initial['email'] == 'prefilled@example.com'
