from django.forms import Select, SelectMultiple
from django.urls import reverse

from taggit.forms import TagWidget
from unfold.widgets import UnfoldAdminTextInputWidget


class _AutocompleteMixin:
    """Add data-autocomplete-url attribute for JS-driven autocomplete widgets"""

    def __init__(self, url_name, *args, **kwargs):
        self.url_name = url_name
        super().__init__(*args, **kwargs)

    def get_url(self):
        return reverse(self.url_name)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-autocomplete-url'] = self.get_url()
        return attrs


class UnfoldTagWidget(UnfoldAdminTextInputWidget):
    """Taggit tag input with unfold styling."""

    def format_value(self, value):
        if isinstance(value, str):
            return value
        if value is not None:
            return ', '.join(tag.tag.name if hasattr(tag, 'tag') else str(tag) for tag in value)
        return ''


class AutocompleteSelect(_AutocompleteMixin, Select):
    pass


class AutocompleteSelectMultiple(_AutocompleteMixin, SelectMultiple):
    pass


class AutocompleteTag(_AutocompleteMixin, TagWidget):
    """Tag input with autocomplete suggestions and free-form tag creation."""
