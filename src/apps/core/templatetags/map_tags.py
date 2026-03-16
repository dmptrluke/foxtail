from django import template
from django.conf import settings

register = template.Library()


@register.filter
def map_style_url(style_name):
    """Return MapTiler style JSON URL, or empty string if no API key is configured"""
    api_key = settings.MAPTILER_API_KEY
    if not api_key:
        return ''
    return f'https://api.maptiler.com/maps/{style_name}/style.json?key={api_key}'
