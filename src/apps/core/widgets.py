from django.conf import settings
from django.forms import Select, SelectMultiple
from django.forms.widgets import ClearableFileInput
from django.urls import reverse

from unfold.widgets import UnfoldAdminTextInputWidget


class ImageWidget(ClearableFileInput):
    """File input with size validation and optional PPOI (point of interest) field"""

    template_name = 'components/forms/widgets/image_widget.html'

    def __init__(self, max_file_size=None, ppoi_field=None, attrs=None, **kwargs):
        if max_file_size is None:
            max_file_size = settings.MAX_IMAGE_FILE_SIZE
        defaults = {'class': 'form-control'}
        if attrs:
            defaults.update(attrs)
        self.max_file_size = max_file_size
        self.ppoi_field = ppoi_field
        super().__init__(attrs=defaults, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update(
            {
                'max_file_size': self.max_file_size,
                'ppoi_field': self.ppoi_field,
            }
        )
        return context


class CroppedImageWidget(ImageWidget):
    """ImageWidget with client-side cropping at a fixed aspect ratio"""

    template_name = 'components/forms/widgets/image_crop.html'

    def __init__(self, aspect_ratio=None, **kwargs):
        self.aspect_ratio = aspect_ratio
        super().__init__(**kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['aspect_ratio'] = self.aspect_ratio
        return context


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
