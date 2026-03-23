import re

from django.urls import reverse

import pytest
from allauth.account.models import EmailAddress
from formguard.test import GuardedFormTestMixin

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPasswordReset(GuardedFormTestMixin):
    url = reverse('account_reset_password')

    @pytest.fixture
    def user_with_email(self):
        user = UserFactory()
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        return user

    # requesting a reset sends an MJML email with reset link and username
    def test_reset_sends_email(self, client, user_with_email, mailoutbox):
        client.post(self.url, {'email': user_with_email.email, **self.guard_data()})
        assert len(mailoutbox) == 1
        msg = mailoutbox[0]
        assert user_with_email.email in msg.to
        assert 'password/reset/key/' in msg.body
        assert user_with_email.username in msg.body
        assert len(msg.alternatives) == 1
        html, mime = msg.alternatives[0]
        assert mime == 'text/html'
        assert '<mjml>' not in html
        assert 'password/reset/key/' in html

    # full flow: request reset, follow email link, set new password, login works
    def test_full_reset_flow(self, client, user_with_email, mailoutbox):
        client.post(self.url, {'email': user_with_email.email, **self.guard_data()})

        reset_url = re.search(r'(https?://\S+/password/reset/key/\S+/)', mailoutbox[0].body).group(1)
        reset_path = re.sub(r'https?://[^/]+', '', reset_url)

        response = client.get(reset_path)
        assert response.status_code == 302
        set_password_path = response['Location']

        new_password = 'NewSecureP@ssw0rd!2026'
        response = client.post(
            set_password_path,
            {
                'password1': new_password,
                'password2': new_password,
            },
        )
        assert response.status_code == 302

        client.logout()
        logged_in = client.login(username=user_with_email.username, password=new_password)
        assert logged_in

    # nonexistent email gets same 302 and an email (no enumeration leak)
    def test_nonexistent_email_no_enumeration(self, client, mailoutbox):
        response = client.post(self.url, {'email': 'nobody@example.com', **self.guard_data()})
        assert response.status_code == 302
        assert len(mailoutbox) == 1
        assert 'password/reset/key/' not in mailoutbox[0].body
