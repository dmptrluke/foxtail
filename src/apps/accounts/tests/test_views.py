from django.contrib.messages import get_messages
from django.test import RequestFactory
from django.urls import reverse

import pytest
from allauth.account.models import EmailAddress
from allauth.idp.oidc.models import Client as OIDCClient
from allauth.idp.oidc.models import Token as OIDCToken
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount

from apps.accounts.views import UserView

pytestmark = pytest.mark.django_db


@pytest.fixture
def oidc_client(db):
    return OIDCClient.objects.create(name='Test App')


@pytest.fixture
def oidc_token(user, oidc_client):
    return OIDCToken.objects.create(
        type=OIDCToken.Type.ACCESS_TOKEN,
        hash='test-hash-1',
        client=oidc_client,
        user=user,
    )


class TestUserView:
    """Test the user settings view (profile edit form)."""

    # get_object() returns the logged-in user
    def test_authenticated(self, user, request_factory: RequestFactory):
        view = UserView()

        request = request_factory.get('/accounts/')
        request.user = user

        view.request = request

        assert view.get_object() == user

    # anonymous users are redirected to login
    def test_unauthenticated(self, client):
        url = reverse('account_profile')

        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == f'/accounts/login/?next={url}'

    # valid POST saves changes to the database
    def test_form_valid_updates_user(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse('account_profile_edit'),
            {
                'username': user.username,
                'full_name': 'New Name',
            },
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.full_name == 'New Name'

    # valid POST redirects back to settings
    def test_form_valid_redirects_to_settings(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse('account_profile_edit'),
            {
                'username': user.username,
                'full_name': 'New Name',
            },
        )
        assert response['Location'] == reverse('account_profile_edit')

    # valid POST shows a success message
    def test_form_valid_shows_success_message(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse('account_profile_edit'),
            {
                'username': user.username,
                'full_name': 'New Name',
            },
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        assert any('updated' in str(m) for m in messages)

    # invalid POST re-renders the form (no redirect)
    def test_form_invalid_rerenders(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse('account_profile_edit'),
            {
                'username': 'root',
            },
        )
        assert response.status_code == 200


class TestDashboardView:
    """Test the account dashboard context (email, MFA, social, apps)."""

    # anonymous users are redirected to login
    def test_requires_login(self, client):
        url = reverse('account_profile')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response['Location']

    # context includes primary email and email count
    def test_context_email_info(self, client, user):
        client.force_login(user)
        email = EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        response = client.get(reverse('account_profile'))
        assert response.context['primary_email'] == email
        assert response.context['email_count'] == 1

    # TOTP authenticator shows MFA as enabled and appears in mfa_methods
    def test_context_mfa_enabled(self, client, user):
        client.force_login(user)
        Authenticator.objects.create(user=user, type=Authenticator.Type.TOTP, data={})
        response = client.get(reverse('account_profile'))
        assert response.context['mfa_enabled'] is True
        assert Authenticator.Type.TOTP in response.context['mfa_methods']

    # recovery codes alone don't count as MFA enabled (they're a fallback, not a factor)
    def test_context_mfa_excludes_recovery_codes(self, client, user):
        client.force_login(user)
        Authenticator.objects.create(user=user, type=Authenticator.Type.RECOVERY_CODES, data={})
        response = client.get(reverse('account_profile'))
        assert response.context['mfa_enabled'] is False

    # context includes social account count and provider names
    def test_context_social_info(self, client, user):
        client.force_login(user)
        SocialAccount.objects.create(user=user, provider='discord', uid='123', extra_data={})
        response = client.get(reverse('account_profile'))
        assert response.context['social_count'] == 1
        assert 'discord' in response.context['social_providers']

    # authorized OIDC apps are counted by distinct client
    def test_context_app_count(self, client, user, oidc_token):
        client.force_login(user)
        response = client.get(reverse('account_profile'))
        assert response.context['app_count'] == 1

    # has_password reflects whether the user has a usable password
    def test_context_has_password(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_profile'))
        assert response.context['has_password'] is True

    # new user with no data gets zeroed-out defaults
    def test_context_defaults_empty(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_profile'))
        assert response.context['email_count'] == 0
        assert response.context['mfa_enabled'] is False
        assert response.context['app_count'] == 0
        assert response.context['social_count'] == 0


class TestConsentList:
    """Test the OIDC authorized applications list view."""

    # anonymous users are redirected to login
    def test_requires_login(self, client):
        url = reverse('account_application_list')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response['Location']

    # lists the user's authorized OIDC clients
    def test_shows_own_clients(self, client, user, oidc_client, oidc_token):
        client.force_login(user)
        response = client.get(reverse('account_application_list'))
        assert oidc_client in response.context['client_list']

    # other users' authorized apps are not visible (queryset scoped to logged-in user)
    def test_excludes_other_users(self, client, user, second_user, oidc_client):
        OIDCToken.objects.create(
            type=OIDCToken.Type.ACCESS_TOKEN,
            hash='other-hash',
            client=oidc_client,
            user=second_user,
        )
        client.force_login(user)
        response = client.get(reverse('account_application_list'))
        assert list(response.context['client_list']) == []

    # no authorized apps shows an empty list
    def test_empty_when_no_tokens(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_application_list'))
        assert response.status_code == 200
        assert list(response.context['client_list']) == []


class TestConsentRevoke:
    """Test revoking OIDC application consent and token cleanup."""

    # anonymous users are redirected to login
    def test_requires_login(self, client, oidc_client):
        url = reverse('account_application_revoke', kwargs={'pk': oidc_client.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert '/login/' in response['Location']

    # revoke deletes tokens and redirects to app list
    def test_revoke_deletes_tokens(self, client, user, oidc_client, oidc_token):
        client.force_login(user)
        url = reverse('account_application_revoke', kwargs={'pk': oidc_client.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('account_application_list')
        assert not OIDCToken.objects.filter(user=user, client=oidc_client).exists()

    # nonexistent client pk returns 404
    def test_revoke_404_nonexistent_client(self, client, user):
        client.force_login(user)
        url = reverse('account_application_revoke', kwargs={'pk': 'nonexistent'})
        response = client.post(url)
        assert response.status_code == 404

    # 404 when user has no tokens for the client
    def test_revoke_404_no_tokens_for_user(self, client, user, oidc_client):
        client.force_login(user)
        url = reverse('account_application_revoke', kwargs={'pk': oidc_client.pk})
        response = client.post(url)
        assert response.status_code == 404

    # revoke only deletes the requesting user's tokens, other users' tokens survive
    def test_revoke_doesnt_affect_other_users(self, client, user, second_user, oidc_client, oidc_token):
        other_token = OIDCToken.objects.create(
            type=OIDCToken.Type.ACCESS_TOKEN,
            hash='other-hash',
            client=oidc_client,
            user=second_user,
        )
        client.force_login(user)
        url = reverse('account_application_revoke', kwargs={'pk': oidc_client.pk})
        client.post(url)
        assert OIDCToken.objects.filter(pk=other_token.pk).exists()


class TestChangePassword:
    """Test password change/set view routing based on password state."""

    # user without a password can access the set-password form
    def test_set_password(self, client, user_without_password):
        client.force_login(user_without_password)

        url = reverse('account_set_password')
        response = client.get(url)
        assert response.status_code == 200

    # user with a password can access the change-password form
    def test_change_password(self, client, user):
        client.force_login(user)

        url = reverse('account_change_password')
        response = client.get(url)
        assert response.status_code == 200

    # no password: change-password redirects to set-password
    def test_change_to_set(self, client, user_without_password):
        client.force_login(user_without_password)

        url = reverse('account_change_password')
        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == reverse('account_set_password')

    # has password: set-password redirects to change-password
    def test_set_to_change(self, client, user):
        client.force_login(user)

        url = reverse('account_set_password')
        response = client.get(url)

        assert response.status_code == 302
        assert response['Location'] == reverse('account_change_password')
