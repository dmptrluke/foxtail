from unittest.mock import Mock

import pytest
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount, SocialLogin

from apps.telegram.models import TelegramLink
from apps.telegram.signals import on_social_account_changed, on_social_account_removed


def _make_sociallogin(provider, uid, extra_data=None, user=None):
    account = Mock()
    account.provider = provider
    account.uid = uid
    account.extra_data = extra_data or {}
    sociallogin = Mock()
    sociallogin.account = account
    sociallogin.user = user
    return sociallogin


def _make_socialaccount(provider, uid, user=None):
    account = Mock()
    account.provider = provider
    account.uid = uid
    account.user_id = user.pk if user else None
    return account


@pytest.mark.django_db
class TestSocialAccountChanged:
    # first-time social signups create the bot link through the registered signup receiver
    def test_first_telegram_signup_creates_link(self, user, request_factory):
        extra = {'id_token': {'id': '12345', 'preferred_username': 'tguser', 'name': 'Test', 'sub': 'oidc-sub'}}
        account = SocialAccount.objects.create(user=user, provider='telegram', uid='12345', extra_data=extra)
        sociallogin = SocialLogin(user=user, account=account)

        user_signed_up.send(sender=type(user), request=request_factory.get('/'), user=user, sociallogin=sociallogin)

        link = TelegramLink.objects.get(user=user)
        assert link.telegram_id == 12345
        assert link.username == 'tguser'
        account.refresh_from_db()
        assert account.extra_data == extra

    # password signups do not create Telegram identities
    def test_password_signup_ignored(self, user, request_factory):
        user_signed_up.send(sender=type(user), request=request_factory.get('/'), user=user)
        assert not TelegramLink.objects.exists()
        assert not SocialAccount.objects.filter(provider='telegram').exists()

    # long OAuth display names fit the bot-link name field
    def test_long_oauth_name(self, user):
        extra = {'id_token': {'name': 'x' * 100}}
        sociallogin = _make_sociallogin('telegram', '12345', extra, user=user)
        on_social_account_changed(sender=None, request=Mock(user=user), sociallogin=sociallogin)
        assert TelegramLink.objects.get(user=user).name == 'x' * 64

    # creates TelegramLink and SocialAccount from uid (real Telegram ID)
    def test_creates_link(self, user):
        request = Mock(user=user)
        extra = {'id_token': {'id': '12345', 'preferred_username': 'tguser', 'name': 'Test'}}
        sociallogin = _make_sociallogin('telegram', '12345', extra, user=user)
        on_social_account_changed(sender=None, request=request, sociallogin=sociallogin)
        link = TelegramLink.objects.get(telegram_id=12345)
        assert link.user == user
        assert link.username == 'tguser'
        assert link.name == 'Test'
        assert SocialAccount.objects.filter(provider='telegram', uid='12345', user=user).exists()

    # non-telegram provider is ignored
    def test_ignores_non_telegram(self, user):
        request = Mock(user=user)
        sociallogin = _make_sociallogin('github', '99999', user=user)
        on_social_account_changed(sender=None, request=request, sociallogin=sociallogin)
        assert not TelegramLink.objects.filter(user=user).exists()

    # updates existing link (idempotent)
    def test_updates_existing(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345, username='old')
        request = Mock(user=user)
        extra = {'id_token': {'id': '12345', 'preferred_username': 'new', 'name': 'Updated'}}
        sociallogin = _make_sociallogin('telegram', '12345', extra, user=user)
        on_social_account_changed(sender=None, request=request, sociallogin=sociallogin)
        link = TelegramLink.objects.get(telegram_id=12345)
        assert link.username == 'new'
        assert link.name == 'Updated'


@pytest.mark.django_db
class TestSocialAccountRemoved:
    # disconnecting a sign-in account removes only its matching bot link
    def test_deletes_link(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        request = Mock(user=user)
        socialaccount = _make_socialaccount('telegram', '12345', user=user)
        on_social_account_removed(sender=None, request=request, socialaccount=socialaccount)
        assert not TelegramLink.objects.filter(telegram_id=12345).exists()
        assert not SocialAccount.objects.filter(provider='telegram', uid='12345').exists()

    # disconnecting a conflicting sign-in account cannot delete another user's bot link
    def test_preserves_other_owner_link(self, user, second_user, telegram_link_factory):
        link = telegram_link_factory(user=second_user, telegram_id=12345)
        socialaccount = _make_socialaccount('telegram', '12345', user=user)
        on_social_account_removed(sender=None, request=Mock(user=user), socialaccount=socialaccount)
        assert TelegramLink.objects.filter(pk=link.pk, user=second_user).exists()

    # non-telegram provider is ignored
    def test_ignores_non_telegram(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        request = Mock(user=user)
        socialaccount = _make_socialaccount('github', '12345')
        on_social_account_removed(sender=None, request=request, socialaccount=socialaccount)
        assert TelegramLink.objects.filter(telegram_id=12345).exists()
