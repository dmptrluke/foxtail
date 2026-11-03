from importlib import import_module

from django.apps import apps
from django.db import connection

import pytest
from allauth.socialaccount.models import SocialAccount

from apps.telegram.models import TelegramLink

backfill_links = import_module('apps.telegram.migrations.0008_backfill_missing_telegram_links').backfill_links
pytestmark = pytest.mark.django_db


# backfill creates the missing link once and preserves the original OAuth metadata
def test_backfills_missing_link(user):
    claims = {'id_token': {'id': '12345', 'preferred_username': 'tguser', 'name': 'Telegram User'}}
    account = SocialAccount.objects.create(user=user, provider='telegram', uid='12345', extra_data=claims)

    backfill_links(apps, connection.schema_editor())
    backfill_links(apps, connection.schema_editor())

    link = TelegramLink.objects.get(user=user)
    assert link.telegram_id == 12345
    assert link.username == 'tguser'
    assert link.name == 'Telegram User'
    assert TelegramLink.objects.count() == 1
    account.refresh_from_db()
    assert account.extra_data == claims


# backfill leaves conflicting owners and existing bot-link state untouched
def test_preserves_conflicting_links(user, second_user, telegram_link_factory):
    account = SocialAccount.objects.create(user=user, provider='telegram', uid='12345')
    existing = telegram_link_factory(user=second_user, telegram_id=12345, username='keep', is_blocked=True)
    SocialAccount.objects.create(user=second_user, provider='telegram', uid='67890')

    backfill_links(apps, connection.schema_editor())

    existing.refresh_from_db()
    assert existing.user_id == second_user.pk
    assert existing.telegram_id == 12345
    assert existing.username == 'keep'
    assert existing.is_blocked
    assert TelegramLink.objects.count() == 1
    account.refresh_from_db()
    assert account.user_id == user.pk
