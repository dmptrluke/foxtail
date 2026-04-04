from django.conf import settings
from django.forms.widgets import ClearableFileInput


class ImageWidget(ClearableFileInput):
    """File input with size validation and optional PPOI (point of interest) field"""

    template_name = 'components/forms/widgets/image_widget.html'

    def __init__(self, max_file_size=None, ppoi_field=None, attrs=None, **kwargs):
        if max_file_size is None:
            max_file_size = settings.MAX_IMAGE_FILE_SIZE
        defaults = {'class': 'd-none'}
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
    """ImageWidget with client-side cropping, optionally at a fixed aspect ratio."""

    def __init__(self, aspect_ratio=None, preview_round=False, **kwargs):
        self.aspect_ratio = aspect_ratio
        self.preview_round = preview_round
        super().__init__(**kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['crop'] = True
        context['widget']['aspect_ratio'] = self.aspect_ratio
        context['widget']['preview_round'] = self.preview_round
        return context
