from unittest.mock import patch

from django.db import IntegrityError

import pytest
from allauth.socialaccount.models import SocialAccount

from apps.telegram import linking
from apps.telegram.models import TelegramLink


@pytest.mark.django_db
class TestLink:
    # a failed social-account write does not leave a partial bot link
    def test_rolls_back_on_social_account_failure(self, user):
        with (
            patch.object(SocialAccount, 'save', side_effect=RuntimeError('write failed')),
            pytest.raises(RuntimeError, match='write failed'),
        ):
            linking.link(user, 12345)
        assert not TelegramLink.objects.exists()
        assert not SocialAccount.objects.filter(provider='telegram').exists()

    # an existing OAuth account cannot be transferred to another user through bot linking
    def test_rejects_other_social_account_owner(self, user, second_user):
        account = SocialAccount.objects.create(provider='telegram', uid='12345', user=second_user)
        with pytest.raises(IntegrityError, match='belongs to another user'):
            linking.link(user, 12345)
        account.refresh_from_db()
        assert account.user == second_user
        assert not TelegramLink.objects.exists()

    # an existing bot link cannot be reassigned to another user
    def test_rejects_other_link_owner(self, user, second_user, telegram_link_factory):
        link = telegram_link_factory(user=second_user, telegram_id=12345)
        with pytest.raises(IntegrityError, match='already linked to another user'):
            linking.link(user, 12345)
        link.refresh_from_db()
        assert link.user == second_user
        assert not SocialAccount.objects.filter(provider='telegram').exists()

    # an existing sign-in identity prevents linking a different Telegram account through the bot
    def test_rejects_another_telegram_identity(self, user):
        SocialAccount.objects.create(provider='telegram', uid='111', user=user)
        with pytest.raises(IntegrityError, match='another Telegram sign-in account'):
            linking.link(user, 222)
        assert not TelegramLink.objects.exists()
        assert list(SocialAccount.objects.values_list('uid', flat=True)) == ['111']

    # refreshing the bot link preserves the OAuth claims used by account screens and sign-in
    def test_preserves_oauth_metadata(self, user):
        extra = {'id_token': {'id': '12345', 'preferred_username': 'tguser', 'sub': 'oidc-sub'}}
        account = SocialAccount.objects.create(provider='telegram', uid='12345', user=user, extra_data=extra)
        linking.link(user, 12345, username='tguser')
        account.refresh_from_db()
        assert account.extra_data == extra

    # creates both TelegramLink and SocialAccount
    def test_creates_both(self, user):
        linking.link(user, 12345, username='tguser', name='Test')
        assert TelegramLink.objects.filter(telegram_id=12345, user=user).exists()
        assert SocialAccount.objects.filter(provider='telegram', uid='12345', user=user).exists()

    # updates TelegramLink, SocialAccount unchanged
    def test_update_existing(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345, username='old')
        SocialAccount.objects.create(provider='telegram', uid='12345', user=user, extra_data={})

        linking.link(user, 12345, username='new', name='Updated')
        link = TelegramLink.objects.get(telegram_id=12345)
        assert link.username == 'new'
        assert link.name == 'Updated'
        assert SocialAccount.objects.filter(provider='telegram', uid='12345').count() == 1


@pytest.mark.django_db
class TestUnlink:
    # deletes both TelegramLink and SocialAccount
    def test_deletes_both(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        SocialAccount.objects.create(provider='telegram', uid='12345', user=user, extra_data={})

        assert linking.unlink(12345) is True
        assert not TelegramLink.objects.filter(telegram_id=12345).exists()
        assert not SocialAccount.objects.filter(provider='telegram', uid='12345').exists()

    # returns False when nothing to unlink
    def test_returns_false_when_missing(self):
        assert linking.unlink(99999) is False

    # handles TelegramLink without SocialAccount (bot-only link)
    def test_no_social_account(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        assert linking.unlink(12345) is True
        assert not TelegramLink.objects.filter(telegram_id=12345).exists()
