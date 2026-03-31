"""Web app -> Telegram API. Direct calls, no queue."""

from . import api


def send_message(telegram_id, text):
    api.send_message(chat_id=telegram_id, text=text)
