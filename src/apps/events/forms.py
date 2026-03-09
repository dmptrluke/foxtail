from django.forms import DateInput, DateTimeField, DateTimeInput, ImageField, ModelForm, Textarea, TimeInput

from taggit.forms import TagField

from apps.core.widgets import CroppedImageWidget

from .models import Event


class EventForm(ModelForm):
    tags = TagField(required=False, help_text='Comma-separated list of tags.')
    image = ImageField(required=False, widget=CroppedImageWidget(aspect_ratio=2))
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
        ]
        widgets = {
            'description': Textarea(attrs={'rows': 10}),
            'address': Textarea(attrs={'rows': 5}),
            'start': DateInput(attrs={'type': 'date'}),
            'end': DateInput(attrs={'type': 'date'}),
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = ', '.join(self.instance.tags.values_list('name', flat=True))
