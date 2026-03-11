from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, format_html_join

register = template.Library()


@register.simple_tag
def breadcrumbs(*args):
    """Render a Bootstrap 5 breadcrumb nav from alternating url/label pairs.

    The last argument (odd) is the current page label (no link).
    Each URL argument is tried with reverse() first; if that fails
    (e.g. URL requires kwargs), it's treated as a pre-resolved URL.

    Usage: {% breadcrumbs "account_profile" "Account" "mfa_index" "Two-Factor Auth" "Add Key" %}
    """
    args = list(args)
    current = args.pop() if len(args) % 2 == 1 else None

    items = []
    for url_or_name, label in zip(args[::2], args[1::2], strict=True):
        try:
            url = reverse(url_or_name)
        except NoReverseMatch:
            url = url_or_name
        items.append((url, label))

    linked = format_html_join(
        '',
        '<li class="breadcrumb-item"><a href="{}">{}</a></li>',
        items,
    )

    if current:
        linked = format_html(
            '{}<li class="breadcrumb-item active" aria-current="page">{}</li>',
            linked,
            current,
        )

    return format_html(
        '<nav aria-label="Breadcrumb"><ol class="breadcrumb">{}</ol></nav>',
        linked,
    )
