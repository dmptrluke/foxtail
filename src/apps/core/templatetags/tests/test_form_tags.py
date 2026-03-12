from unittest.mock import MagicMock

from ..form_tags import _UNSET, _set_widget_attrs, plain_errors


class TestSetWidgetAttrs:
    def _make_field(self, **initial_attrs):
        field = MagicMock()
        field.field.widget.attrs = dict(initial_attrs)
        return field

    # sets a widget attribute to the given value
    def test_sets_attribute_value(self):
        field = self._make_field()
        _set_widget_attrs(field, placeholder='Enter text')
        assert field.field.widget.attrs['placeholder'] == 'Enter text'

    # None removes the attribute from the widget
    def test_removes_attribute_when_none(self):
        field = self._make_field(autocomplete='on')
        _set_widget_attrs(field, autocomplete=None)
        assert 'autocomplete' not in field.field.widget.attrs

    # _UNSET sentinel leaves existing attributes untouched
    def test_skips_unset_sentinel(self):
        field = self._make_field(placeholder='original')
        _set_widget_attrs(field, placeholder=_UNSET)
        assert field.field.widget.attrs['placeholder'] == 'original'


class TestPlainErrors:
    # joins multiple error messages with semicolons
    def test_joins_errors(self):
        assert plain_errors(['Error 1', 'Error 2']) == 'Error 1; Error 2'

    # single error returns without separator
    def test_single_error(self):
        assert plain_errors(['Only error']) == 'Only error'
