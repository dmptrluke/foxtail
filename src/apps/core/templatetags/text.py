import html as html_module
import math

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def reading_time(html):
    """Estimate reading time from HTML content at 200 words per minute"""
    if not html:
        return '1 min read'
    text = strip_tags(str(html))
    words = len(text.split())
    minutes = max(1, math.ceil(words / 200))
    return f'{minutes} min read'


@register.filter
def plain_text(html):
    """Strip HTML tags and decode entities to plain text"""
    if not html:
        return ''
    return html_module.unescape(strip_tags(str(html)))


@register.filter
def initials(name):
    """Extract up to 2 initials from a name"""
    if not name:
        return ''
    name = str(name)
    words = name.split()
    if len(words) > 1:
        return ''.join(w[0] for w in words[:2]).upper()
    caps = [c for c in name if c.isupper()]
    if caps:
        return ''.join(caps[:2])
    return name[:2].upper()
