from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def recaptcha_head(context):
    host = getattr(settings, 'RECAPTCHA_HOST', 'https://recaptcha.net')
    nonce = context.request.csp_nonce

    html = '<script src ="{0}/recaptcha/api.js" nonce="{1}" async defer></script>'
    return format_html(html, host, nonce)


@register.simple_tag()
def recaptcha_widget():
    key = settings.RECAPTCHA_PUBLIC_KEY

    html = '<div class="g-recaptcha" data-sitekey="{0}"></div>'
    return format_html(html, key)
