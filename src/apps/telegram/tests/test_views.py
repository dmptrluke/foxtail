from django.urls import reverse

import pytest
from allauth.socialaccount.models import SocialAccount

from apps.telegram.models import TelegramLink


@pytest.mark.django_db
class TestLinkTelegramView:
    # anonymous user redirected to login
    def test_anonymous_redirected(self, client, link_token_factory):
        token = link_token_factory()
        url = reverse('telegram_link', kwargs={'token': token.token})
        resp = client.get(url)
        assert resp.status_code == 302
        assert '/accounts/login/' in resp.url

    # valid token shows confirmation page
    def test_valid_token(self, client, user, link_token_factory):
        client.force_login(user)
        token = link_token_factory(telegram_username='testbot')
        url = reverse('telegram_link', kwargs={'token': token.token})
        resp = client.get(url)
        assert resp.status_code == 200
        assert b'@testbot' in resp.content

    # expired token redirects with error
    def test_expired_token(self, client, user, expired_link_token_factory):
        client.force_login(user)
        token = expired_link_token_factory()
        url = reverse('telegram_link', kwargs={'token': token.token})
        resp = client.get(url, follow=True)
        assert b'expired' in resp.content.lower()

    # invalid token returns 404
    def test_invalid_token(self, client, user):
        client.force_login(user)
        url = reverse('telegram_link', kwargs={'token': 'nonexistent'})
        resp = client.get(url)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestLinkTelegramConfirmView:
    # successful link creation
    def test_confirm_creates_link(self, client, user, link_token_factory):
        client.force_login(user)
        token = link_token_factory(telegram_id=123456)
        resp = client.post(reverse('telegram_link_confirm'), {'token': token.token}, follow=True)
        assert TelegramLink.objects.filter(user=user, telegram_id=123456).exists()
        assert b'linked successfully' in resp.content.lower()

    # token is deleted after successful link
    def test_token_deleted_after_link(self, client, user, link_token_factory):
        client.force_login(user)
        token = link_token_factory()
        from apps.telegram.models import LinkToken

        client.post(reverse('telegram_link_confirm'), {'token': token.token})
        assert not LinkToken.objects.filter(pk=token.pk).exists()

    # expired token on POST shows error
    def test_confirm_expired(self, client, user, expired_link_token_factory):
        client.force_login(user)
        token = expired_link_token_factory()
        resp = client.post(reverse('telegram_link_confirm'), {'token': token.token}, follow=True)
        assert not TelegramLink.objects.filter(user=user).exists()
        assert b'expired' in resp.content.lower()

    # telegram_id already linked to another user
    def test_telegram_id_already_linked(self, client, user, second_user, link_token_factory, telegram_link_factory):
        client.force_login(user)
        telegram_link_factory(user=second_user, telegram_id=999)
        token = link_token_factory(telegram_id=999)
        resp = client.post(reverse('telegram_link_confirm'), {'token': token.token}, follow=True)
        assert not TelegramLink.objects.filter(user=user).exists()
        assert b'already linked' in resp.content.lower()

    # user already has a link
    def test_user_already_linked(self, client, user, link_token_factory, telegram_link_factory):
        client.force_login(user)
        telegram_link_factory(user=user, telegram_id=111)
        token = link_token_factory(telegram_id=222)
        resp = client.post(reverse('telegram_link_confirm'), {'token': token.token}, follow=True)
        assert b'already linked' in resp.content.lower()

    # confirm creates SocialAccount alongside TelegramLink
    def test_confirm_creates_social_account(self, client, user, link_token_factory):
        client.force_login(user)
        token = link_token_factory(telegram_id=123456)
        client.post(reverse('telegram_link_confirm'), {'token': token.token})
        assert SocialAccount.objects.filter(provider='telegram', uid='123456', user=user).exists()

    # invalid token on POST returns 404
    def test_confirm_invalid_token(self, client, user):
        client.force_login(user)
        resp = client.post(reverse('telegram_link_confirm'), {'token': 'nonexistent'})
        assert resp.status_code == 404
