from django import template

register = template.Library()


@register.filter
def ppoi_position(ppoi):
    """Convert a PPOI string like '0.3x0.7' to CSS object-position like '30% 70%'."""
    if not ppoi:
        return '50% 50%'
    try:
        x, y = ppoi.split('x')
        return f'{float(x) * 100:.0f}% {float(y) * 100:.0f}%'
    except (ValueError, AttributeError):
        return '50% 50%'
