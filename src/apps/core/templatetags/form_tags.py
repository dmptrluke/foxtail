from django import template
from django.forms import MultiWidget

register = template.Library()


def _field_context(field, **extra):
    """ Builds the base template context, adding is_multiwidget for layout decisions """
    return {
        'field': field,
        'is_multiwidget': isinstance(field.field.widget, MultiWidget),
        **extra,
    }


def _set_widget_attrs(field, **attrs):
    """ Sets HTML attributes on the field's widget, skipping any that are not defined """
    for key, value in attrs.items():
        if value is not None:
            field.field.widget.attrs[key] = value


@register.inclusion_tag('components/forms/text_field.html')
def text_field(field, hide_label=False, autocomplete=None, placeholder=None):
    _set_widget_attrs(field, autocomplete=autocomplete, placeholder=placeholder)
    return _field_context(field, hide_label=hide_label)


@register.inclusion_tag('components/forms/check_field.html')
def check_field(field, hide_label=False):
    return _field_context(field, hide_label=hide_label)


@register.inclusion_tag('components/forms/select_field.html')
def select_field(field, hide_label=False):
    return _field_context(field, hide_label=hide_label)


@register.inclusion_tag('components/forms/textarea_field.html')
def textarea_field(field, hide_label=False, autocomplete=None, placeholder=None, rows=None):
    _set_widget_attrs(field, autocomplete=autocomplete, placeholder=placeholder, rows=rows)
    return _field_context(field, hide_label=hide_label)


@register.inclusion_tag('components/forms/captcha_field.html')
def captcha_field(field):
    return _field_context(field)
