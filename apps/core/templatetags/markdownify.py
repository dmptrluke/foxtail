from django import template
from django.conf import settings

from markdown import markdown

register = template.Library()


@register.filter(name='markdown')
def markdown_tag(content):
    extensions = getattr(settings, 'MARKDOWN_EXTENSIONS', [])
    extension_configs = getattr(settings, 'MARKDOWN_EXTENSION_CONFIGS', [])

    md = markdown(
        text=content,
        extensions=extensions,
        extension_configs=extension_configs
    )

    return md
