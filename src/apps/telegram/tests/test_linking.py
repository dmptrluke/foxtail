import pytest
from allauth.socialaccount.models import SocialAccount

from apps.telegram import linking
from apps.telegram.models import TelegramLink


@pytest.mark.django_db
class TestLink:
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
