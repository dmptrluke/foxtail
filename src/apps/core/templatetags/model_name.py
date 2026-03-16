from django import template

register = template.Library()


@register.filter
def get_model_name(value):
    """Return the class name of a model instance for template branching"""
    return str(value.__class__.__name__)
