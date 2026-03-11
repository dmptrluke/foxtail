from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from structured_data.util import json_encode

register = template.Library()


def _resolve(url_or_name):
    try:
        return reverse(url_or_name)
    except NoReverseMatch:
        return url_or_name


@register.simple_tag(takes_context=True)
def breadcrumbs(context, *args):
    """Render a Bootstrap 5 breadcrumb nav + JSON-LD from alternating url/label pairs.

    All arguments are url/label pairs. The last pair is the current page
    (rendered as active, no link). URLs are tried with reverse() first,
    falling back to literal strings.

    Usage: {% breadcrumbs "events:list" "Events" event.get_absolute_url event.title %}
    """
    crumbs = [(_resolve(url), str(label)) for url, label in zip(args[::2], args[1::2], strict=True)]

    # Visual nav
    lis = format_html_join('', '<li class="breadcrumb-item"><a href="{}">{}</a></li>', crumbs[:-1])
    lis += format_html('<li class="breadcrumb-item active" aria-current="page">{}</li>', crumbs[-1][1])
    nav = format_html('<nav aria-label="Breadcrumb"><ol class="breadcrumb">{}</ol></nav>', lis)

    # JSON-LD
    site_url = context.get('SITE_URL', '')
    ld = json_encode(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'name': name, 'item': f'{site_url}{url}'}
                for i, (url, name) in enumerate(crumbs, 1)
            ],
        }
    )

    return format_html('{}<script type="application/ld+json">{}</script>', nav, mark_safe(ld))  # noqa: S308
