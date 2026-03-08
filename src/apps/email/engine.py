# Inspired by django-celery-email by Paul McLanahan (BSD licensed)
# https://github.com/pmclanahan/django-celery-email

import logging

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

import django_rq
from rq import Retry

logger = logging.getLogger(__name__)


def send_message_async(message, **kwargs):
    conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
    conn.open()
    try:
        conn.send_messages([message])
        logger.info('Sent email to %r', message.to)
    finally:
        conn.close()


class AsyncEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, messages):
        for message in messages:
            try:
                django_rq.enqueue(
                    send_message_async,
                    message,
                    retry=Retry(max=3, interval=[10, 60, 300]),
                    description=f'Email to {message.to}',
                    **self.init_kwargs,
                )
            except Exception:
                if not self.fail_silently:
                    raise
                logger.exception('Failed to enqueue email to %r', message.to)
        return len(messages)
