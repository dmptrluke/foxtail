import json
from unittest.mock import patch

from django.urls import reverse

import pytest

WEBHOOK_SECRET = 'test-webhook-secret'
WEBHOOK_URL = reverse('telegram_webhook')


def _post_update(client, update, secret=WEBHOOK_SECRET):
    return client.post(
        WEBHOOK_URL,
        data=json.dumps(update),
        content_type='application/json',
        headers={'X-Telegram-Bot-Api-Secret-Token': secret},
    )


def _make_update(command, telegram_id=12345, chat_type='private'):
    return {
        'update_id': 1,
        'message': {
            'message_id': 1,
            'from': {
                'id': telegram_id,
                'is_bot': False,
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser',
            },
            'chat': {'id': telegram_id, 'type': chat_type},
            'date': 1700000000,
            'text': command,
        },
    }


@pytest.fixture(autouse=True)
def _telegram_settings(settings):
    settings.TELEGRAM_WEBHOOK_SECRET = WEBHOOK_SECRET
    settings.TELEGRAM_BOT_TOKEN = 'fake-token'


@pytest.mark.django_db
class TestTelegramWebhook:
    # wrong secret returns 403
    def test_wrong_secret_rejected(self, client):
        resp = _post_update(client, _make_update('/ping'), secret='wrong')
        assert resp.status_code == 403

    # missing secret returns 403
    def test_missing_secret_rejected(self, client):
        resp = client.post(
            WEBHOOK_URL,
            data=json.dumps(_make_update('/ping')),
            content_type='application/json',
        )
        assert resp.status_code == 403

    # invalid JSON returns 400
    def test_invalid_json(self, client):
        resp = client.post(
            WEBHOOK_URL,
            data='not json',
            content_type='application/json',
            headers={'X-Telegram-Bot-Api-Secret-Token': WEBHOOK_SECRET},
        )
        assert resp.status_code == 400

    # valid update returns 200
    @patch('apps.telegram.api.send_message')
    def test_valid_update_returns_ok(self, mock_send, client):
        resp = _post_update(client, _make_update('/ping'))
        assert resp.status_code == 200

    # non-command message is ignored
    @patch('apps.telegram.api.send_message')
    def test_non_command_ignored(self, mock_send, client):
        resp = _post_update(client, _make_update('hello'))
        assert resp.status_code == 200
        mock_send.assert_not_called()

    # non-message update is ignored
    @patch('apps.telegram.api.send_message')
    def test_non_message_update_ignored(self, mock_send, client):
        resp = _post_update(client, {'update_id': 1})
        assert resp.status_code == 200
        mock_send.assert_not_called()

    # /ping dispatches and sends pong
    @patch('apps.telegram.api.send_message')
    def test_ping_command(self, mock_send, client):
        _post_update(client, _make_update('/ping'))
        mock_send.assert_called_once_with(12345, 'pong')

    # /start dispatches and sends greeting
    @patch('apps.telegram.api.send_message')
    def test_start_command(self, mock_send, client):
        _post_update(client, _make_update('/start'))
        mock_send.assert_called_once()
        assert 'Kia ora' in mock_send.call_args[0][1]

    # /help dispatches and sends command list
    @patch('apps.telegram.api.send_message')
    def test_help_command(self, mock_send, client):
        _post_update(client, _make_update('/help'))
        mock_send.assert_called_once()
        text = mock_send.call_args[0][1]
        assert '/link' in text
        assert '/status' in text

    # /link in group chat is rejected
    @patch('apps.telegram.api.send_message')
    def test_link_in_group_rejected(self, mock_send, client):
        _post_update(client, _make_update('/link', chat_type='group'))
        mock_send.assert_called_once()
        assert 'private chat' in mock_send.call_args[0][1]

    # /link creates a LinkToken
    @patch('apps.telegram.api.send_message')
    def test_link_creates_token(self, mock_send, client):
        _post_update(client, _make_update('/link', telegram_id=99999))
        from apps.telegram.models import LinkToken

        assert LinkToken.objects.filter(telegram_id=99999).exists()

    # /link when already linked shows message
    @patch('apps.telegram.api.send_message')
    def test_link_already_linked(self, mock_send, client, telegram_link_factory):
        telegram_link_factory(telegram_id=88888)
        _post_update(client, _make_update('/link', telegram_id=88888))
        assert 'already linked' in mock_send.call_args[0][1]

    # /status shows linked account
    @patch('apps.telegram.api.send_message')
    def test_status_linked(self, mock_send, client, telegram_link_factory):
        link = telegram_link_factory(telegram_id=77777)
        _post_update(client, _make_update('/status', telegram_id=77777))
        assert link.user.username in mock_send.call_args[0][1]

    # /status when not linked
    @patch('apps.telegram.api.send_message')
    def test_status_not_linked(self, mock_send, client):
        _post_update(client, _make_update('/status', telegram_id=66666))
        assert 'not linked' in mock_send.call_args[0][1]

    # /unlink removes link
    @patch('apps.telegram.api.send_message')
    def test_unlink(self, mock_send, client, telegram_link_factory):
        telegram_link_factory(telegram_id=55555)
        _post_update(client, _make_update('/unlink', telegram_id=55555))
        from apps.telegram.models import TelegramLink

        assert not TelegramLink.objects.filter(telegram_id=55555).exists()
        assert 'unlinked' in mock_send.call_args[0][1]

    # /unlink when not linked
    @patch('apps.telegram.api.send_message')
    def test_unlink_not_linked(self, mock_send, client):
        _post_update(client, _make_update('/unlink', telegram_id=44444))
        assert 'not linked' in mock_send.call_args[0][1]

    # user data sync updates TelegramLink on message
    @patch('apps.telegram.api.send_message')
    def test_user_data_synced(self, mock_send, client, telegram_link_factory):
        telegram_link_factory(telegram_id=33333, username='old_name', name='Old Name')
        _post_update(client, _make_update('/ping', telegram_id=33333))
        from apps.telegram.models import TelegramLink

        link = TelegramLink.objects.get(telegram_id=33333)
        assert link.username == 'testuser'
        assert link.name == 'Test User'

    # command with @botname suffix is dispatched correctly
    @patch('apps.telegram.api.send_message')
    def test_command_with_bot_suffix(self, mock_send, client):
        _post_update(client, _make_update('/ping@furry_nz_bot'))
        mock_send.assert_called_once_with(12345, 'pong')
