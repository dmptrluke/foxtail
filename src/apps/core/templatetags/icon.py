from django import template
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


@register.simple_tag(name='icon')
def icon_tag(icon_id, tag='div', size=None, colored=False):
    # abuse the django slugify function to clean file names
    icon_id = slugify(icon_id)
    prefix = 'colored/' if colored else ''
    cache_key = f'icon4_{prefix}{icon_id}'

    # see if we've already handled and loaded this icon before
    cached_icon = cache.get(cache_key)

    if cached_icon:
        icon_data = cached_icon
    else:
        # no cached icon, damn. now I have to work with files
        icon_path = finders.find(f'icons/{prefix}{icon_id}.svg')
        if not icon_path:
            return ''

        with open(icon_path) as icon_file:
            icon_data = icon_file.read()

            cache.set(cache_key, icon_data, None)

    if size:
        # Inject inline style on the SVG to override SCSS dimensions
        icon_data = icon_data.replace('<svg ', f'<svg style="width:{size};height:{size}" ', 1)

    return format_html(
        """
        <{0} class='icon icon-{1} svg-baseline'>
            {2}
        </{0}>
        """,
        tag,
        icon_id,
        mark_safe(icon_data),  # noqa: S308
    )
