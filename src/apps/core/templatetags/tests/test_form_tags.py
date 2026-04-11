from unittest.mock import MagicMock

from ..form_tags import _UNSET, _render_context, check_field, prefix_field


def _make_field(**initial_attrs):
    field = MagicMock()
    field.field.widget.attrs = dict(initial_attrs)
    field.field.widget.__class__ = type('TextInput', (), {})
    field.use_fieldset = False
    field.errors = []
    field.help_text = ''
    return field


class TestWidgetAttrs:
    # sets a widget attribute to the given value
    def test_sets_attribute_value(self):
        field = _make_field()
        _render_context(field, widget_attrs={'placeholder': 'Enter text'})
        assert field.field.widget.attrs['placeholder'] == 'Enter text'

    # None removes the attribute from the widget
    def test_removes_attribute_when_none(self):
        field = _make_field(autocomplete='on')
        _render_context(field, widget_attrs={'autocomplete': None})
        assert 'autocomplete' not in field.field.widget.attrs

    # _UNSET sentinel leaves existing attributes untouched
    def test_skips_unset_sentinel(self):
        field = _make_field(placeholder='original')
        _render_context(field, widget_attrs={'placeholder': _UNSET})
        assert field.field.widget.attrs['placeholder'] == 'original'


class TestErrors:
    # joins multiple error messages with semicolons
    def test_joins_errors(self):
        field = _make_field()
        field.errors = ['Error 1', 'Error 2']
        result = _render_context(field)
        assert result['errors'] == 'Error 1; Error 2'

    # single error returns without separator
    def test_single_error(self):
        field = _make_field()
        field.errors = ['Only error']
        result = _render_context(field)
        assert result['errors'] == 'Only error'

    # no errors returns empty string
    def test_no_errors(self):
        field = _make_field()
        result = _render_context(field)
        assert result['errors'] == ''


class TestCheckField:
    # returns context with field, hide_label, and inline keys
    def test_returns_render_context(self):
        field = _make_field()
        result = check_field(field, hide_label=True, inline=True)
        assert result['field'] is field
        assert result['hide_label'] is True
        assert result['inline'] is True
        assert 'use_multiwidget' in result


class TestPrefixField:
    # returns context with field, prefix, and hide_label keys
    def test_returns_render_context(self):
        field = _make_field()
        result = prefix_field(field, prefix='@', hide_label=True)
        assert result['field'] is field
        assert result['prefix'] == '@'
        assert result['hide_label'] is True
        assert 'use_multiwidget' in result
