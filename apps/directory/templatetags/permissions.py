"""
Modified versions of the standard django_rules template tags.
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_perm(context, perm, on=None):
    user = context.request.user
    if not hasattr(user, 'has_perm'):
        return False
    else:
        return user.has_perm(perm, on)


@register.simple_tag(takes_context=True)
def can_view(context, field, on):
    model_name = on.__class__.__name__
    perm = f'view_{model_name}_{field}'.lower()
    print('checking', perm)
    return has_perm(context, perm, on)
