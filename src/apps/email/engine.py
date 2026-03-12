# Inspired by django-celery-email by Paul McLanahan (BSD licensed)
# https://github.com/pmclanahan/django-celery-email

import logging

from django.core.mail.backends.base import BaseEmailBackend

from apps.email.tasks import send_email_message

logger = logging.getLogger(__name__)


class AsyncEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages):
        sent = 0
        for msg in email_messages:
            try:
                send_email_message(msg, **self.init_kwargs)
                sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
                logger.exception('Failed to enqueue email to %d recipient(s)', len(msg.to))
        return sent
