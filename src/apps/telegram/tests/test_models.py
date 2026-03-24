from datetime import timedelta

from django.db import IntegrityError
from django.utils.timezone import now

import pytest


@pytest.mark.django_db
class TestLinkToken:
    # future expiry returns False
    def test_not_expired(self, link_token_factory):
        token = link_token_factory(expires_at=now() + timedelta(hours=1))
        assert not token.is_expired

    # past expiry returns True
    def test_expired(self, link_token_factory):
        token = link_token_factory(expires_at=now() - timedelta(minutes=1))
        assert token.is_expired

    # token field enforces uniqueness
    def test_token_unique(self, link_token_factory):
        token = link_token_factory()
        with pytest.raises(IntegrityError):
            link_token_factory(token=token.token)


@pytest.mark.django_db
class TestTelegramLink:
    # telegram_id is unique across links
    def test_telegram_id_unique(self, telegram_link_factory):
        link = telegram_link_factory()
        with pytest.raises(IntegrityError):
            telegram_link_factory(telegram_id=link.telegram_id)

    # one user can only have one link (OneToOneField)
    def test_user_unique(self, telegram_link_factory):
        link = telegram_link_factory()
        with pytest.raises(IntegrityError):
            telegram_link_factory(user=link.user)
