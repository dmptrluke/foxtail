from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def recaptcha_head(context):
    nonce = context.request.csp_nonce

    html = '<script src ="http://www.google.com/recaptcha/api.js" nonce="{0}" async defer></script>'
    return format_html(html, nonce)


@register.simple_tag()
def recaptcha_widget():
    key = settings.RECAPTCHA_PUBLIC_KEY

    html = '<div class="g-recaptcha" data-sitekey="{0}"></div>'
    return format_html(html, key)
