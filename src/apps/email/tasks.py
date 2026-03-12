import logging

from django.conf import settings
from django.core.mail import get_connection

from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)


@task(retries=3, retry_delay=60)
def send_email_message(message, **kwargs):
    conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
    with conn:
        conn.send_messages([message])
    logger.info('Sent email to %d recipient(s)', len(message.to))
