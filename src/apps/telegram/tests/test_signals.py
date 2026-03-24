from unittest.mock import Mock

import pytest
from allauth.socialaccount.models import SocialAccount

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


def _make_socialaccount(provider, uid):
    account = Mock()
    account.provider = provider
    account.uid = uid
    return account


@pytest.mark.django_db
class TestSocialAccountChanged:
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
    # deletes TelegramLink and SocialAccount
    def test_deletes_link(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        SocialAccount.objects.create(provider='telegram', uid='12345', user=user, extra_data={})
        request = Mock(user=user)
        socialaccount = _make_socialaccount('telegram', '12345')
        on_social_account_removed(sender=None, request=request, socialaccount=socialaccount)
        assert not TelegramLink.objects.filter(telegram_id=12345).exists()
        assert not SocialAccount.objects.filter(provider='telegram', uid='12345').exists()

    # non-telegram provider is ignored
    def test_ignores_non_telegram(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        request = Mock(user=user)
        socialaccount = _make_socialaccount('github', '12345')
        on_social_account_removed(sender=None, request=request, socialaccount=socialaccount)
        assert TelegramLink.objects.filter(telegram_id=12345).exists()
