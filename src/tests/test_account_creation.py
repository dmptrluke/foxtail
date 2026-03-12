from django.contrib.messages import get_messages
from django.urls import reverse

import pytest

from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestAccountCreation:
    url = reverse('account_signup')

    # valid signup creates user and redirects to homepage
    def test_signup_creates_user_and_redirects(self, client):
        proto_user = UserFactory.build()
        response = client.post(
            self.url,
            {
                'username': proto_user.username,
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
            },
        )
        assert response.status_code == 302
        assert response['Location'] == reverse('content:index')
        assert User.objects.filter(username=proto_user.username).exists()

    # successful signup shows sign-in success message
    def test_signup_shows_success_message(self, client):
        proto_user = UserFactory.build()
        response = client.post(
            self.url,
            {
                'username': proto_user.username,
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
            },
            follow=True,
        )
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        assert any(f'Successfully signed in as {proto_user.username}' in m for m in messages)
