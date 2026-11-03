"""Render multipart emails using allauth-style template prefixes.

Each prefix has _subject.txt, _message.txt, and _message.mjml templates.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string

from mjml import mjml2html


def mjml_template_exists(template_prefix):
    """Return a MJML body template exists for the given prefix"""
    try:
        get_template(f'{template_prefix}_message.mjml')
    except TemplateDoesNotExist:
        return False
    return True


def build_message(template_prefix, to, context, from_email=None, headers=None):
    """Render subject, text, and MJML templates into a multipart email"""
    from apps.core.models import SiteSettings

    context = {'SITE_URL': settings.SITE_URL, 'conf': SiteSettings.get_solo(), **context}

    subject = render_to_string(f'{template_prefix}_subject.txt', context)
    subject = ' '.join(subject.splitlines()).strip()
    text_body = render_to_string(f'{template_prefix}_message.txt', context)
    html_body = mjml2html(render_to_string(f'{template_prefix}_message.mjml', context))

    message = EmailMultiAlternatives(subject, text_body, from_email, to, headers=headers)
    message.attach_alternative(html_body, 'text/html')
    return message


def send_email(template_prefix, to, context, from_email=None):
    """Render and send an email through the configured backend"""
    build_message(template_prefix, to, context, from_email).send()
