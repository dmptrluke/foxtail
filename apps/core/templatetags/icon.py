import os.path

from django import template
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


@register.simple_tag(name='icon')
def icon_tag(icon_id):
    # abuse the django slugify function to clean file names
    icon_id = slugify(icon_id)

    # see if we've already handled and loaded this icon before
    cached_icon = cache.get(f'icon_{icon_id}')

    if cached_icon:
        return mark_safe(cached_icon)

    # no cached icon, damn. now I have to work with files
    icon_path = finders.find(f'icons/{icon_id}.svg')

    if not os.path.isfile(icon_path):
        # yeet
        raise FileNotFoundError

    with open(icon_path) as icon_file:
        html = format_html("""
        <div class='icon icon-{0} svg-baseline'>
            {1}
        </div>
        """, icon_id, mark_safe(icon_file.read()))

        cache.set(f'icon_{icon_id}', html, None)

    return html
