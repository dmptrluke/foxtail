from django.forms import (
    DateInput,
    DateTimeField,
    DateTimeInput,
    HiddenInput,
    ImageField,
    ModelForm,
    Textarea,
    TimeInput,
)

from csp_helpers.mixins import CSPFormMixin
from markdownfield.widgets import MDEWidget
from taggit.forms import TagField

from apps.core.widgets import CroppedImageWidget

from .models import Event


class EventForm(CSPFormMixin, ModelForm):
    tags = TagField(required=False, help_text='Comma-separated list of tags.')
    image = ImageField(required=False, widget=CroppedImageWidget(aspect_ratio=2, ppoi_field='image_ppoi'))
    live_as_of = DateTimeField(
        required=False,
        label='Publish Date',
        help_text='Required when status is "Available after Publish Date".',
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'url',
            'location',
            'address',
            'start',
            'start_time',
            'end',
            'end_time',
            'publish_status',
            'live_as_of',
            'image',
            'image_ppoi',
        ]
        widgets = {
            'description': MDEWidget(),
            'address': Textarea(attrs={'rows': 5}),
            'start': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'start_time': TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'end_time': TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'image_ppoi': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()
