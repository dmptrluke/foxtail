from django import template
from django.forms import MultiWidget

register = template.Library()

# distinguishes "not passed" from explicitly passing None.
_UNSET = object()


def _field_context(field, **extra):
    # Builds the base template context, adding is_multiwidget for layout decisions.
    return {
        'field': field,
        'is_multiwidget': isinstance(field.field.widget, MultiWidget),
        **extra,
    }


def _set_widget_attrs(field, **attrs):
    # Sets HTML attributes on the field's widget.
    # _UNSET = leave the form's value untouched.
    # None   = remove the attribute entirely.
    # value  = set to that value.
    for key, value in attrs.items():
        if value is _UNSET:
            pass
        elif value is None:
            field.field.widget.attrs.pop(key, None)
        else:
            field.field.widget.attrs[key] = value


@register.inclusion_tag('components/forms/text_field.html')
def text_field(field, hide_label=False, inline=False, autocomplete=_UNSET, placeholder=_UNSET):
    _set_widget_attrs(field, autocomplete=autocomplete, placeholder=placeholder)
    return _field_context(field, hide_label=hide_label, inline=inline)


@register.inclusion_tag('components/forms/check_field.html')
def check_field(field, hide_label=False, inline=False):
    return _field_context(field, hide_label=hide_label, inline=inline)


@register.inclusion_tag('components/forms/select_field.html')
def select_field(field, hide_label=False, inline=False):
    return _field_context(field, hide_label=hide_label, inline=inline)


@register.inclusion_tag('components/forms/textarea_field.html')
def textarea_field(field, hide_label=False, inline=False, autocomplete=_UNSET, placeholder=_UNSET, rows=_UNSET):
    _set_widget_attrs(field, autocomplete=autocomplete, placeholder=placeholder, rows=rows)
    return _field_context(field, hide_label=hide_label, inline=inline)


@register.inclusion_tag('components/forms/captcha_field.html')
def captcha_field(field):
    return _field_context(field)


@register.inclusion_tag('components/forms/image_field.html')
def image_field(field, hide_label=False):
    return _field_context(field, hide_label=hide_label)


@register.inclusion_tag('components/forms/prefix_field.html')
def prefix_field(field, prefix, hide_label=False, autocomplete=_UNSET, placeholder=_UNSET):
    _set_widget_attrs(field, autocomplete=autocomplete, placeholder=placeholder)
    return _field_context(field, hide_label=hide_label, prefix=prefix)


@register.filter
def plain_errors(errors):
    return '; '.join(errors)


@register.inclusion_tag('components/forms/non_field_errors.html')
def non_field_errors(form):
    return {'form': form}


@register.inclusion_tag('components/forms/honeypot_field.html')
def honeypot_field(field):
    _set_widget_attrs(field, tabindex='-1', autocomplete='one-time-code')
    return {'field': field}
