"""Thin wrapper around the Telegram Bot API. Each function is a single POST request."""

import logging

from django.conf import settings

import requests

logger = logging.getLogger(__name__)

API_BASE = 'https://api.telegram.org/bot{token}/{method}'


def _call(method, **params):
    """POST to Telegram Bot API. Returns response dict or None on error."""
    url = API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    try:
        resp = requests.post(url, json=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get('result')
    except requests.RequestException:
        logger.exception('Telegram API error: %s', method)
        return None


def send_message(chat_id, text, parse_mode='HTML'):
    return _call('sendMessage', chat_id=chat_id, text=text, parse_mode=parse_mode)


def set_my_commands(commands):
    """commands: list of {'command': str, 'description': str}"""
    return _call('setMyCommands', commands=commands)


def set_webhook(url, secret_token=None, drop_pending_updates=False):
    params = {'url': url, 'drop_pending_updates': drop_pending_updates}
    if secret_token:
        params['secret_token'] = secret_token
    return _call('setWebhook', **params)


def delete_webhook(drop_pending_updates=False):
    return _call('deleteWebhook', drop_pending_updates=drop_pending_updates)
