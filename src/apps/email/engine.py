# Inspired by django-celery-email by Paul McLanahan (BSD licensed)
# https://github.com/pmclanahan/django-celery-email

import logging

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.template.loader import render_to_string

from mjml import mjml2html

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


def render_email(subject, to, template, context, from_email=None, headers=None):
    from apps.core.models import SiteSettings

    context.setdefault('conf', SiteSettings.get_solo())
    text_body = render_to_string(f'{template}.txt', context)
    mjml_source = render_to_string(f'{template}.mjml', context)
    html_body = mjml2html(mjml_source)

    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, 'text/html')
    if headers:
        msg.extra_headers.update(headers)
    return msg


def send_email(subject, to, template, context, from_email=None):
    msg = render_email(subject, to, template, context, from_email)
    msg.send()
