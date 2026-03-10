from django.forms.widgets import ClearableFileInput


class ImageWidget(ClearableFileInput):
    template_name = 'components/forms/widgets/image_widget.html'

    def __init__(self, max_file_size=5 * 1024 * 1024, ppoi_field=None, attrs=None, **kwargs):
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
    template_name = 'components/forms/widgets/image_crop.html'

    def __init__(self, aspect_ratio=None, **kwargs):
        self.aspect_ratio = aspect_ratio
        super().__init__(**kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['aspect_ratio'] = self.aspect_ratio
        return context
