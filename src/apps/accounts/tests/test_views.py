import re

from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.test import RequestFactory
from django.urls import reverse

import pytest
from allauth.account.models import EmailAddress
from allauth.idp.oidc.models import Client as OIDCClient
from allauth.idp.oidc.models import Token as OIDCToken
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount

from apps.accounts.models import Verification
from apps.accounts.views import (
    VERIFICATION_TOKEN_TTL,
    UserView,
    _cache_key_for_token,
    _cache_key_for_user,
    _generate_token,
    _normalize_token,
)

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


@pytest.fixture
def verifier(second_user):
    # uses second_user so `user` is free as the verification target
    group, _ = Group.objects.get_or_create(name='verifiers')
    second_user.groups.add(group)
    return second_user


@pytest.fixture
def verification(user, verifier):
    return Verification.objects.create(user=user, verified_by=verifier)


@pytest.fixture
def token():
    return _generate_token()


def _store_token(token, user_id):
    cache.set(_cache_key_for_token(token), user_id, VERIFICATION_TOKEN_TTL)
    cache.set(_cache_key_for_user(user_id), token, VERIFICATION_TOKEN_TTL)


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

    # context includes primary email
    def test_context_email_info(self, client, user):
        client.force_login(user)
        email = EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        response = client.get(reverse('account_profile'))
        assert response.context['primary_email'] == email

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

    # context includes social account count
    def test_context_social_info(self, client, user):
        client.force_login(user)
        SocialAccount.objects.create(user=user, provider='discord', uid='123', extra_data={})
        response = client.get(reverse('account_profile'))
        assert response.context['social_count'] == 1

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
        assert response.context['primary_email'] is None
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


class TestTokenHelpers:
    """Test verification token generation and normalization functions."""

    # generated token matches XXXX-XXXX format with uppercase alphanumeric chars
    def test_generate_token_format(self):
        token = _generate_token()
        assert re.fullmatch(r'[A-Z0-9]{4}-[A-Z0-9]{4}', token)

    # generated tokens are not identical (randomness sanity check)
    def test_generate_token_uniqueness(self):
        tokens = {_generate_token() for _ in range(10)}
        assert len(tokens) > 1

    # lowercase input without dash is normalized to XXXX-XXXX uppercase
    def test_normalize_strips_dashes_and_uppercases(self):
        assert _normalize_token('abcd1234') == 'ABCD-1234'

    # already-formatted input is preserved
    def test_normalize_preserves_valid_format(self):
        assert _normalize_token('ABCD-1234') == 'ABCD-1234'

    # wrong-length input is uppercased but not reformatted
    def test_normalize_wrong_length_passthrough(self):
        assert _normalize_token('abc') == 'ABC'

    # dash in a non-standard position is stripped and reformatted correctly
    def test_normalize_misplaced_dash(self):
        assert _normalize_token('AB-CD1234') == 'ABCD-1234'


class TestVerificationView:
    """Test the verification status page and token display."""

    # anonymous users are redirected to login
    def test_requires_login(self, client):
        url = reverse('account_verification')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response['Location']

    # unverified user has no verification object in context
    def test_unverified_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_verification'))
        assert response.status_code == 200
        assert 'verification' not in response.context

    # verified user sees their verification object
    def test_verified_user_sees_verification(self, client, user, verification):
        client.force_login(user)
        response = client.get(reverse('account_verification'))
        assert response.context['verification'] == verification

    # active token in cache is shown with QR code and TTL
    def test_shows_active_token(self, client, user, token):
        client.force_login(user)
        _store_token(token, user.pk)
        response = client.get(reverse('account_verification'))
        assert response.context['token'] == token
        assert 'token_ttl' in response.context
        assert response.context['qr_data_uri'].startswith('data:image/svg+xml;base64,')

    # stale user→token pointer with expired token cache doesn't show token
    def test_expired_token_not_shown(self, client, user):
        client.force_login(user)
        cache.set(_cache_key_for_user(user.pk), 'DEAD-BEEF', VERIFICATION_TOKEN_TTL)
        response = client.get(reverse('account_verification'))
        assert 'token' not in response.context

    # verifier user sees is_verifier=True
    def test_verifier_flag(self, client, verifier):
        client.force_login(verifier)
        response = client.get(reverse('account_verification'))
        assert response.context['is_verifier'] is True

    # regular user sees is_verifier=False
    def test_non_verifier_flag(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_verification'))
        assert response.context['is_verifier'] is False

    # ?code= query param prefills lookup form for verifiers
    def test_code_prefill_for_verifier(self, client, verifier):
        client.force_login(verifier)
        response = client.get(reverse('account_verification') + '?code=ABCD-1234')
        assert response.context['prefilled_code'] == 'ABCD-1234'

    # ?code= for non-verifier shows error message, no prefill
    def test_code_prefill_denied_for_non_verifier(self, client, user):
        client.force_login(user)
        response = client.get(reverse('account_verification') + '?code=ABCD-1234')
        assert 'prefilled_code' not in response.context
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('permission' in m for m in msgs)


class TestGenerateTokenView:
    """Test verification token generation endpoint."""

    # anonymous users are redirected to login
    def test_requires_login(self, client):
        url = reverse('account_verification_generate')
        response = client.post(url)
        assert response.status_code == 302
        assert '/login/' in response['Location']

    # POST creates both cache keys (token→user_id and user_id→token)
    def test_generates_token_in_cache(self, client, user):
        client.force_login(user)
        client.post(reverse('account_verification_generate'))
        token = cache.get(_cache_key_for_user(user.pk))
        assert token is not None
        assert cache.get(_cache_key_for_token(token)) == user.pk

    # POST redirects to verification page
    def test_redirects_to_verification(self, client, user):
        client.force_login(user)
        response = client.post(reverse('account_verification_generate'))
        assert response.status_code == 302
        assert response['Location'] == reverse('account_verification')

    # generating a new token invalidates the old one and creates a valid replacement
    def test_replaces_old_token(self, client, user):
        client.force_login(user)
        _store_token('OLD1-OLD2', user.pk)
        client.post(reverse('account_verification_generate'))
        assert cache.get(_cache_key_for_token('OLD1-OLD2')) is None
        new_token = cache.get(_cache_key_for_user(user.pk))
        assert new_token != 'OLD1-OLD2'
        assert re.fullmatch(r'[A-Z0-9]{4}-[A-Z0-9]{4}', new_token)
        assert cache.get(_cache_key_for_token(new_token)) == user.pk

    # returns 429 after exceeding verify_generate rate limit
    @pytest.mark.keep_rate_limits
    def test_rate_limited(self, client, user, settings):
        settings.ACCOUNT_RATE_LIMITS = {'verify_generate': '5/m/user'}
        client.force_login(user)
        for _ in range(6):
            response = client.post(reverse('account_verification_generate'))
        assert response.status_code == 429


class TestConfirmVerificationView:
    """Test the verification confirmation page (verifier enters code, sees target user)."""

    # non-verifier gets 403
    def test_requires_verifier_permission(self, client, user):
        client.force_login(user)
        response = client.post(reverse('account_verification_confirm'), {'token': 'ABCD-1234'})
        assert response.status_code == 403

    # valid token shows confirmation page with target user
    def test_valid_token_shows_confirmation(self, client, user, verifier, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_confirm'), {'token': token})
        assert response.status_code == 200
        assert response.context['target_user'] == user
        assert response.context['token'] == token
        assert response.context['already_verified'] is False

    # already-verified user shows already_verified=True on confirmation
    def test_already_verified_flag(self, client, user, verifier, verification, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_confirm'), {'token': token})
        assert response.status_code == 200
        assert response.context['already_verified'] is True

    # expired/invalid token redirects with error message
    def test_invalid_token_redirects(self, client, verifier):
        client.force_login(verifier)
        response = client.post(reverse('account_verification_confirm'), {'token': 'BAD0-CODE'}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('Invalid or expired' in m for m in msgs)

    # empty token redirects with error message
    def test_empty_token_redirects(self, client, verifier):
        client.force_login(verifier)
        response = client.post(reverse('account_verification_confirm'), {'token': ''}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('enter a verification code' in m for m in msgs)

    # verifier cannot confirm their own token
    def test_self_verification_rejected(self, client, verifier, token):
        client.force_login(verifier)
        _store_token(token, verifier.pk)
        response = client.post(reverse('account_verification_confirm'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('cannot verify yourself' in m for m in msgs)


class TestVerifyUserView:
    """Test the endpoint that creates a Verification record."""

    # non-verifier gets 403
    def test_requires_verifier_permission(self, client, user):
        client.force_login(user)
        response = client.post(reverse('account_verification_verify'), {'token': 'ABCD-1234'})
        assert response.status_code == 403

    # valid token creates Verification record with correct verified_by
    def test_creates_verification_record(self, client, user, verifier, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_verify'), {'token': token})
        assert response.status_code == 302
        v = Verification.objects.get(user=user)
        assert v.verified_by == verifier

    # both cache keys are cleaned up after verification
    def test_clears_cache(self, client, user, verifier, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_verify'), {'token': token})
        assert response.status_code == 302
        assert cache.get(_cache_key_for_token(token)) is None
        assert cache.get(_cache_key_for_user(user.pk)) is None

    # verifying already-verified user shows info message, no duplicate record
    def test_already_verified_shows_info(self, client, user, verifier, verification, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_verify'), {'token': token}, follow=True)
        assert Verification.objects.filter(user=user).count() == 1
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('already verified' in m for m in msgs)

    # invalid token redirects with error
    def test_invalid_token_redirects(self, client, verifier):
        client.force_login(verifier)
        response = client.post(reverse('account_verification_verify'), {'token': 'BAD0-CODE'}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('Invalid or expired' in m for m in msgs)

    # successful verification shows success message
    def test_success_message(self, client, user, verifier, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_verify'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('has been verified' in m for m in msgs)

    # verifier cannot verify themselves
    def test_self_verification_rejected(self, client, verifier, token):
        client.force_login(verifier)
        _store_token(token, verifier.pk)
        response = client.post(reverse('account_verification_verify'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('cannot verify yourself' in m for m in msgs)
        assert not Verification.objects.filter(user=verifier).exists()

    # returns 429 after exceeding verify_submit rate limit
    @pytest.mark.keep_rate_limits
    def test_rate_limited(self, client, verifier, settings):
        settings.ACCOUNT_RATE_LIMITS = {'verify_submit': '10/m/ip'}
        client.force_login(verifier)
        for _ in range(11):
            response = client.post(reverse('account_verification_verify'), {'token': 'FAKE-CODE'})
        assert response.status_code == 429


class TestUnverifyUserView:
    """Test the endpoint that removes a Verification record."""

    # non-verifier gets 403
    def test_requires_verifier_permission(self, client, user):
        client.force_login(user)
        response = client.post(reverse('account_verification_unverify'), {'token': 'ABCD-1234'})
        assert response.status_code == 403

    # valid token deletes the Verification record
    def test_deletes_verification_record(self, client, user, verifier, verification, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_unverify'), {'token': token})
        assert response.status_code == 302
        assert not Verification.objects.filter(user=user).exists()

    # both cache keys are cleaned up after unverification
    def test_clears_cache(self, client, user, verifier, verification, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_unverify'), {'token': token})
        assert response.status_code == 302
        assert cache.get(_cache_key_for_token(token)) is None
        assert cache.get(_cache_key_for_user(user.pk)) is None

    # unverifying a non-verified user shows info message
    def test_not_verified_shows_info(self, client, user, verifier, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_unverify'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('not currently verified' in m for m in msgs)

    # invalid token redirects with error
    def test_invalid_token_redirects(self, client, verifier):
        client.force_login(verifier)
        response = client.post(reverse('account_verification_unverify'), {'token': 'BAD0-CODE'}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('Invalid or expired' in m for m in msgs)

    # successful unverification shows success message
    def test_success_message(self, client, user, verifier, verification, token):
        client.force_login(verifier)
        _store_token(token, user.pk)
        response = client.post(reverse('account_verification_unverify'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('has been removed' in m for m in msgs)

    # verifier cannot unverify themselves
    def test_self_unverification_rejected(self, client, verifier, token):
        client.force_login(verifier)
        _store_token(token, verifier.pk)
        response = client.post(reverse('account_verification_unverify'), {'token': token}, follow=True)
        msgs = [str(m) for m in get_messages(response.wsgi_request)]
        assert any('cannot verify yourself' in m for m in msgs)

    # returns 429 after exceeding verify_unverify rate limit
    @pytest.mark.keep_rate_limits
    def test_rate_limited(self, client, verifier, settings):
        settings.ACCOUNT_RATE_LIMITS = {'verify_unverify': '5/m/user'}
        client.force_login(verifier)
        for _ in range(6):
            response = client.post(reverse('account_verification_unverify'), {'token': 'FAKE-CODE'})
        assert response.status_code == 429
