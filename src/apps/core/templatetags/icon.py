from django import template
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


@register.simple_tag(name='icon')
def icon_tag(icon_id, size=None, colored=False):
    # abuse the django slugify function to clean file names
    icon_id = slugify(icon_id)
    prefix = 'colored/' if colored else ''
    cache_key = f'icon5_{prefix}{icon_id}'

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

    attrs = f'class="icon icon-{icon_id}"'
    if size:
        attrs += f' width="{size}" height="{size}"'

    icon_data = icon_data.replace('<svg ', f'<svg {attrs} ', 1)

    return mark_safe(icon_data)  # noqa: S308
