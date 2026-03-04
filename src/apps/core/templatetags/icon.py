from django import template
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


@register.simple_tag(name='icon')
def icon_tag(icon_id, tag='div'):
    # abuse the django slugify function to clean file names
    icon_id = slugify(icon_id)

    # see if we've already handled and loaded this icon before
    cached_icon = cache.get(f'icon3_{icon_id}')

    if cached_icon:
        icon_data = cached_icon
    else:
        # no cached icon, damn. now I have to work with files
        icon_path = finders.find(f'icons/{icon_id}.svg')

        if not icon_path:
            # yeet
            raise FileNotFoundError(f'No icon found for "{icon_id}".')

        with open(icon_path) as icon_file:
            icon_data = icon_file.read()
            cache.set(f'icon3_{icon_id}', icon_data, None)

    return format_html("""
        <{0} class='icon icon-{1} svg-baseline'>
            {2}
        </{0}>
        """, tag, icon_id, mark_safe(icon_data))  # nosec
