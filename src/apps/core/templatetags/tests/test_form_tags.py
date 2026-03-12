from unittest.mock import MagicMock

from ..form_tags import _UNSET, _set_widget_attrs, captcha_field, check_field, plain_errors, prefix_field


def _make_field(**initial_attrs):
    field = MagicMock()
    field.field.widget.attrs = dict(initial_attrs)
    field.field.widget.__class__ = type('TextInput', (), {})
    return field


class TestSetWidgetAttrs:
    # sets a widget attribute to the given value
    def test_sets_attribute_value(self):
        field = _make_field()
        _set_widget_attrs(field, placeholder='Enter text')
        assert field.field.widget.attrs['placeholder'] == 'Enter text'

    # None removes the attribute from the widget
    def test_removes_attribute_when_none(self):
        field = _make_field(autocomplete='on')
        _set_widget_attrs(field, autocomplete=None)
        assert 'autocomplete' not in field.field.widget.attrs

    # _UNSET sentinel leaves existing attributes untouched
    def test_skips_unset_sentinel(self):
        field = _make_field(placeholder='original')
        _set_widget_attrs(field, placeholder=_UNSET)
        assert field.field.widget.attrs['placeholder'] == 'original'


class TestPlainErrors:
    # joins multiple error messages with semicolons
    def test_joins_errors(self):
        assert plain_errors(['Error 1', 'Error 2']) == 'Error 1; Error 2'

    # single error returns without separator
    def test_single_error(self):
        assert plain_errors(['Only error']) == 'Only error'


class TestCheckField:
    # returns context with field, hide_label, and inline keys
    def test_returns_field_context(self):
        field = _make_field()
        result = check_field(field, hide_label=True, inline=True)
        assert result['field'] is field
        assert result['hide_label'] is True
        assert result['inline'] is True
        assert 'is_multiwidget' in result


class TestCaptchaField:
    # returns context with field key
    def test_returns_field_context(self):
        field = _make_field()
        result = captcha_field(field)
        assert result['field'] is field
        assert 'is_multiwidget' in result


class TestPrefixField:
    # returns context with field, prefix, and hide_label keys
    def test_returns_field_context(self):
        field = _make_field()
        result = prefix_field(field, prefix='@', hide_label=True)
        assert result['field'] is field
        assert result['prefix'] == '@'
        assert result['hide_label'] is True
        assert 'is_multiwidget' in result
