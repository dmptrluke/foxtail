from django.forms import (
    DateInput,
    DateTimeField,
    DateTimeInput,
    HiddenInput,
    ImageField,
    ModelForm,
    NumberInput,
    Textarea,
    TimeInput,
    inlineformset_factory,
)

from csp_helpers.mixins import CSPFormMixin
from taggit.forms import TagField

from apps.core.widgets import AutocompleteSelect, AutocompleteTag
from apps.images.widgets import ImageWidget

from .models import Event, EventTicketTier


class EventForm(CSPFormMixin, ModelForm):
    tags = TagField(required=False, widget=AutocompleteTag('autocomplete:tag'))
    image = ImageField(required=False, widget=ImageWidget(ppoi_field='image_ppoi'))
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
            'slug',
            'description',
            'url',
            'organisation',
            'series',
            'location',
            'address',
            'start',
            'start_time',
            'end',
            'end_time',
            'age_requirement',
            'publish_status',
            'live_as_of',
            'image',
            'image_ppoi',
        ]
        widgets = {
            'organisation': AutocompleteSelect('autocomplete:organisation'),
            'series': AutocompleteSelect('autocomplete:event_series'),
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


class EventTicketTierForm(CSPFormMixin, ModelForm):
    available_from = DateTimeField(
        required=False,
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    available_until = DateTimeField(
        required=False,
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = EventTicketTier
        fields = ['name', 'price', 'currency', 'available_from', 'available_until', 'is_sold_out', 'order']
        widgets = {
            'price': NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'order': HiddenInput(),
        }

    def has_changed(self):
        changed = super().has_changed()
        if changed and not self.instance.pk and set(self.changed_data) == {'order'}:
            return False
        return changed


EventTicketTierFormSet = inlineformset_factory(
    Event,
    EventTicketTier,
    form=EventTicketTierForm,
    fields=['name', 'price', 'currency', 'available_from', 'available_until', 'is_sold_out', 'order'],
    extra=1,
    can_delete=True,
)
