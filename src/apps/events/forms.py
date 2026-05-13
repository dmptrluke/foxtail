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
from django.forms.models import BaseInlineFormSet

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
            'order': HiddenInput(attrs={'data-manage-formset-order': ''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_sold_out'].label = 'Sold out'
        self.fields['order'].required = False

    def has_changed(self):
        changed = super().has_changed()
        if changed and not self.instance.pk and set(self.changed_data) == {'order'}:
            return False
        return changed


class EventTicketTierFormSetBase(BaseInlineFormSet):
    order_field_name = 'order'

    def _active_ordered_forms(self):
        ordered_forms = []
        for form_index, form in enumerate(self.forms):
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            if self.can_delete and self._should_delete_form(form):
                continue

            order = form.cleaned_data.get(self.order_field_name)
            if order in (None, ''):
                order = form_index
            ordered_forms.append((order, form_index, form))

        return [form for _, _, form in sorted(ordered_forms, key=lambda item: (item[0], item[1]))]

    def _normalize_orders(self):
        for order, form in enumerate(self._active_ordered_forms()):
            form.cleaned_data[self.order_field_name] = order
            setattr(form.instance, self.order_field_name, order)

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        self._normalize_orders()

    def save(self, commit=True):
        self._normalize_orders()
        result = super().save(commit=commit)
        if commit:
            for form in self._active_ordered_forms():
                if form.instance.pk:
                    form.instance.save(update_fields=[self.order_field_name])
        return result


EventTicketTierFormSet = inlineformset_factory(
    Event,
    EventTicketTier,
    form=EventTicketTierForm,
    formset=EventTicketTierFormSetBase,
    fields=['name', 'price', 'currency', 'available_from', 'available_until', 'is_sold_out', 'order'],
    extra=0,
    can_delete=True,
)
