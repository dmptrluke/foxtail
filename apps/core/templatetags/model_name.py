from django import template

register = template.Library()


@register.filter
def get_model_name(value):
    return str(value.__class__.__name__)
