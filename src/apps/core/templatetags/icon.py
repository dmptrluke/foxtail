from django import template
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from django_cotton import render_component

register = template.Library()


@register.simple_tag(takes_context=True, name='icon')
def icon_tag(context, icon_id, size=None, colored=False):
    """Render an SVG icon Cotton component by name.

    Usage: {% icon "telegram" %} or {% icon "discord" size="1.2em" colored=True %}
    Icons live in templates/cotton/icons/ (colored variants in icons/colored/).
    """
    icon_id = slugify(icon_id)
    prefix = 'colored.' if colored else ''
    component_name = f'icons.{prefix}{icon_id}'

    kwargs = {}
    if size:
        kwargs['width'] = size
        kwargs['height'] = size

    return mark_safe(render_component(context['request'], component_name, **kwargs))  # noqa: S308
