from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()


@register.simple_tag
def breadcrumbs(*args):
    """Render a Bootstrap 5 breadcrumb nav from alternating url/label pairs.

    The last argument (odd) is the current page label (no link).

    Usage: {% breadcrumbs url1 "Label 1" url2 "Label 2" "Current Page" %}
    """
    args = list(args)
    current = args.pop() if len(args) % 2 == 1 else None

    items = format_html_join(
        '',
        '<li class="breadcrumb-item"><a href="{}">{}</a></li>',
        [(url, label) for url, label in zip(args[::2], args[1::2], strict=True)],
    )

    if current:
        items = format_html(
            '{}<li class="breadcrumb-item active" aria-current="page">{}</li>',
            items,
            current,
        )

    return format_html(
        '<nav aria-label="Breadcrumb"><ol class="breadcrumb">{}</ol></nav>',
        items,
    )
