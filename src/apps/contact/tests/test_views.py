from django.contrib.messages import get_messages
from django.urls import reverse

import pytest
from formguard.test import GuardedFormTestMixin

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
            **self.guard_data(website='http://spam.com'),
        }
        response = client.post(self.url, data)

        assert response.status_code == 302
        assert len(mailoutbox) == 0
        assert 'formguard triggered' in caplog.text
        messages = list(get_messages(response.wsgi_request))
        assert any('Your message has been sent' in str(m) for m in messages)

    # tampered or missing token blocks silently
    def test_bad_token_blocks_submission(self, client, mailoutbox, caplog):
        data = {
            'name': 'Bot',
            'email': 'bot@spam.com',
            'message': 'Buy now',
            **self.guard_data(fg_token='tampered-garbage'),
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
