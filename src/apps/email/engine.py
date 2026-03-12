# Inspired by django-celery-email by Paul McLanahan (BSD licensed)
# https://github.com/pmclanahan/django-celery-email

import logging

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)


@task(retries=3, retry_delay=60)
def send_message_async(message, **kwargs):
    conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
    conn.open()
    try:
        conn.send_messages([message])
        logger.info('Sent email to %d recipient(s)', len(message.to))
    finally:
        conn.close()


class AsyncEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, messages):
        for message in messages:
            try:
                send_message_async(message, **self.init_kwargs)
            except Exception:
                if not self.fail_silently:
                    raise
                logger.exception('Failed to enqueue email to %d recipient(s)', len(message.to))
        return len(messages)
