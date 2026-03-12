import logging

from django.conf import settings
from django.core.mail import get_connection

from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)


@task(retries=3, retry_delay=60)
def send_email_message(message, **kwargs):
    count = len(message.to)
    try:
        conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
        with conn:
            sent = conn.send_messages([message])
    except Exception:
        logger.exception('Failed to send email to %d recipient(s) (will retry if attempts remain)', count)
        raise
    if not sent:
        logger.error('Email backend returned failure for %d recipient(s)', count)
        raise RuntimeError(f'Email backend returned failure for {count} recipient(s)')
    logger.info('Sent email to %d recipient(s)', count)
