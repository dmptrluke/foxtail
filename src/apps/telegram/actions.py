"""Web app -> bot communication via Redis."""

import json

from django.conf import settings
from django.db import transaction

import redis

_redis_url = settings.REDIS_URL


def _enqueue(action, payload):
    def _publish():
        r = redis.from_url(_redis_url)
        r.rpush('bot:actions', json.dumps({'action': action, **payload}))

    transaction.on_commit(_publish)


def send_message(telegram_id, text):
    _enqueue(
        'send_message',
        {
            'telegram_id': telegram_id,
            'text': text,
        },
    )
