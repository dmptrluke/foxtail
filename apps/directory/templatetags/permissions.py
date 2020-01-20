"""
Modified versions of the standard django_rules template tags.
"""
from django import template

from ..models.base import BaseModel

register = template.Library()


@register.simple_tag(takes_context=True)
def has_perm(context, perm, on=None):
    user = context.request.user
    if not hasattr(user, 'has_perm'):
        return False
    else:
        return user.has_perm(perm, on)


@register.simple_tag(takes_context=True)
def can_view(context, field, obj: BaseModel = None):
    if obj is None:
        obj = context.get('object', None)
        if obj is None:
            raise ValueError('No object was passed to can_view, and one could not be automatically determined.')

    user = context['request'].user
    return obj.can_view(field, user)
