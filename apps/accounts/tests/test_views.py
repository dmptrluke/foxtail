from django.test import RequestFactory
from django.urls import reverse

import pytest

from apps.accounts.views import UserView

pytestmark = pytest.mark.django_db


class TestUserView:
    def test_authenticated(self, user, request_factory: RequestFactory):
        view = UserView()

        request = request_factory.get("/accounts/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_unauthenticated(self, client):
        url = reverse('account_profile')

        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == f'/accounts/login/?next={url}'


class TestChangePassword:
    def test_set_password(self, client, user_without_password):
        client.force_login(user_without_password)

        url = reverse('account_set_password')
        response = client.get(url)
        assert response.status_code == 200

    def test_change_password(self, client, user):
        client.force_login(user)

        url = reverse('account_change_password')
        response = client.get(url)
        assert response.status_code == 200

    def test_change_to_set(self, client, user_without_password):
        """ user has no password set, so this should redirect to set_password """
        client.force_login(user_without_password)

        url = reverse('account_change_password')
        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == reverse('account_set_password')

    def test_set_to_change(self, client, user):
        """ user has a password set, so this should redirect to change_password """
        client.force_login(user)

        url = reverse('account_set_password')
        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == reverse('account_change_password')
