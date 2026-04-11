from django import template
from django.forms import CheckboxInput, MultiWidget, Select, SelectDateWidget

register = template.Library()

_MULTIWIDGET_TYPES = (MultiWidget, SelectDateWidget)

# distinguishes "not passed" from explicitly passing None.
_UNSET = object()


def _css_class_for(widget):
    """Return the Bootstrap CSS class for a widget type."""
    if isinstance(widget, CheckboxInput):
        return 'form-check-input'
    if isinstance(widget, Select):
        return 'form-select'
    # most widgets just use form-control
    return 'form-control'


def _prepare_widget(field):
    """Set CSS class (with is-invalid on errors) and aria-describedby."""
    widget_attrs = field.field.widget.attrs

    # set CSS class if not already set, and add is-invalid if there are errors
    if 'class' not in widget_attrs:
        css_class = _css_class_for(field.field.widget)
        if field.errors:
            css_class += ' is-invalid'
        widget_attrs['class'] = css_class

    # set aria-describedby to the IDs of the help text and error elements, if they exist
    describedby_ids = []
    if field.help_text:
        describedby_ids.append(f'{field.id_for_label}_helptext')
    if field.errors:
        describedby_ids.append(f'{field.id_for_label}_errors')
    if describedby_ids:
        widget_attrs['aria-describedby'] = ' '.join(describedby_ids)
    else:
        widget_attrs.pop('aria-describedby', None)


def _render_context(field, widget_attrs=None, **extra):
    """Apply widget attrs, prepare the widget for rendering, and return template context."""
    if widget_attrs:
        for key, value in widget_attrs.items():
            if value is _UNSET:
                pass
            elif value is None:
                field.field.widget.attrs.pop(key, None)
            else:
                field.field.widget.attrs[key] = value
    _prepare_widget(field)
    ctx = {
        'field': field,
        'errors': '; '.join(field.errors) if field.errors else '',
        'use_multiwidget': isinstance(field.field.widget, _MULTIWIDGET_TYPES),
        'use_fieldset': getattr(field, 'use_fieldset', False),
    }
    ctx.update(extra)
    return ctx


@register.inclusion_tag('components/forms/text_field.html')
def text_field(field, hide_label=False, inline=False, wrapper_class='', autocomplete=_UNSET, placeholder=_UNSET):
    return _render_context(
        field,
        hide_label=hide_label,
        inline=inline,
        wrapper_class=wrapper_class,
        widget_attrs={'autocomplete': autocomplete, 'placeholder': placeholder},
    )


@register.inclusion_tag('components/forms/check_field.html')
def check_field(field, hide_label=False, inline=False, wrapper_class=''):
    return _render_context(field, hide_label=hide_label, inline=inline, wrapper_class=wrapper_class)


@register.inclusion_tag('components/forms/text_field.html')
def select_field(field, hide_label=False, inline=False, wrapper_class=''):
    return _render_context(field, hide_label=hide_label, inline=inline, wrapper_class=wrapper_class)


@register.inclusion_tag('components/forms/text_field.html')
def textarea_field(
    field, hide_label=False, inline=False, wrapper_class='', autocomplete=_UNSET, placeholder=_UNSET, rows=_UNSET
):
    return _render_context(
        field,
        hide_label=hide_label,
        inline=inline,
        wrapper_class=wrapper_class,
        widget_attrs={'autocomplete': autocomplete, 'placeholder': placeholder, 'rows': rows},
    )


@register.inclusion_tag('components/forms/image_field.html')
def image_field(field, hide_label=False, wrapper_class=''):
    return _render_context(field, hide_label=hide_label, wrapper_class=wrapper_class)


@register.inclusion_tag('components/forms/prefix_field.html')
def prefix_field(field, prefix, hide_label=False, wrapper_class='', autocomplete=_UNSET, placeholder=_UNSET):
    return _render_context(
        field,
        hide_label=hide_label,
        prefix=prefix,
        wrapper_class=wrapper_class,
        widget_attrs={'autocomplete': autocomplete, 'placeholder': placeholder},
    )


@register.inclusion_tag('components/forms/non_field_errors.html')
def non_field_errors(form):
    errors = form.non_field_errors()
    return {'errors': '; '.join(errors) if errors else ''}
