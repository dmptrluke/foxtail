from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def reading_time(html):
    if not html:
        return '1 min read'
    text = strip_tags(str(html))
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f'{minutes} min read'
