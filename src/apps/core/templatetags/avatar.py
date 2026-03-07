import logging

from django import template
from django.utils.html import escape

logger = logging.getLogger(__name__)

register = template.Library()

_RENDITION_MAP = [
    (80, 'small'),
    (160, 'medium'),
    (320, 'medium_2x'),
    (400, 'large'),
]


@register.filter
def avatar_url(user, size=40):
    size = int(size)
    if user.avatar:
        try:
            for threshold, format_name in _RENDITION_MAP:
                if size <= threshold:
                    return getattr(user.avatar, format_name)
            return user.avatar.large
        except Exception:
            logger.warning('Failed to load avatar for user %s', user.pk)
    return _default_avatar(user, size)


def _default_avatar(user, size):
    initial = escape((user.get_short_name() or '?')[0].upper())
    hue = (user.pk * 137) % 360
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">'
        f'<rect width="100%" height="100%" fill="hsl({hue},40%,60%)"/>'
        f'<text x="50%" y="50%" dy=".1em" fill="white" text-anchor="middle" '
        f'dominant-baseline="central" font-family="sans-serif" '
        f'font-size="{size * 0.45}">{initial}</text></svg>'
    )
    return 'data:image/svg+xml,' + svg.replace('#', '%23')
