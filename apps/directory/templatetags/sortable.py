from urllib.parse import urlencode

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def sortable_heading(context, **kwargs):
    # Build the url
    query = {'order_by': kwargs['column']}

    # Build the HTML
    if context.get('order_by') == kwargs['column']:
        ordering = context.get('ordering')
        if ordering == 'desc':
            query['ordering'] = 'asc'
        else:
            query['ordering'] = 'desc'

        html = format_html("""
         <th scope="col" class="active {0}">
             <a href="?{1}" class="text-reset">
                 {2}
             </a>
         </th>
             """, ordering, urlencode(query), kwargs['name'])
    else:
        # We are NOT currently sorting by this column!
        query['ordering'] = 'asc'

        html = format_html("""
         <th scope="col">
             <a href="?{0}" class="text-reset">
                 {1}
             </a>
         </th>
             """, urlencode(query), kwargs['name'])

    # Output HTML
    return html
