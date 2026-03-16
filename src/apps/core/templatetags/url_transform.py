from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_transform(context, **kwargs):
    """Merge kwargs into the current query string; None values remove the key.

    Usage: <a href="?{% url_transform page=2 %}">  (preserves other params like ?q=foo)
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        if v is None:
            del query[k]
        else:
            query[k] = v
    return query.urlencode()
