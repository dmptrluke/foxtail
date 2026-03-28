from django.contrib import admin
from django.db import transaction
from django.forms import ModelForm

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeDateFilter, RelatedDropdownFilter
from unfold.decorators import display

from apps.core.admin_helpers import publish_status_badge as _publish_status_badge
from apps.core.widgets import UnfoldTagWidget

from .models import Event, EventInterest
from .tasks import geocode_event


class EventInterestInline(TabularInline):
    model = EventInterest
    extra = 0
    show_count = True
    readonly_fields = ('user', 'status', 'created')


class EventAdminForm(ModelForm):
    class Meta:
        widgets = {
            'tags': UnfoldTagWidget,
        }


class EventAdmin(UnfoldModelAdmin):
    form = EventAdminForm
    warn_unsaved_form = True
    compressed_fields = True
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'tags',
                    'description',
                    'url',
                    'organisation',
                    'series',
                    'age_requirement',
                ),
            },
        ),
        (
            'Location',
            {
                'classes': ['tab'],
                'fields': ('location', 'address', 'latitude', 'longitude'),
            },
        ),
        (
            'Time and Date',
            {
                'classes': ['tab'],
                'fields': ('start', 'start_time', 'end', 'end_time'),
            },
        ),
        (
            'Publishing',
            {
                'classes': ['tab'],
                'fields': ('publish_status', 'live_as_of', 'publish_status_badge'),
            },
        ),
        (
            'Image',
            {
                'classes': ['tab'],
                'fields': ('image', 'image_ppoi'),
            },
        ),
    )

    readonly_fields = ['publish_status_badge']

    @admin.display(description='Current status')
    def publish_status_badge(self, obj):
        return _publish_status_badge(obj)

    inlines = [EventInterestInline]
    autocomplete_fields = ['organisation', 'series']
    search_fields = ['title']
    list_display = ('title', 'organisation', 'start', 'end', 'show_status', 'tag_list')
    list_filter_submit = True
    list_filter = [
        ('start', RangeDateFilter),
        ('organisation', RelatedDropdownFilter),
    ]

    @display(
        description='Status',
        label={
            'Never Available': 'danger',
            'Available': 'success',
            'Available after "Publish Date"': 'info',
        },
    )
    def show_status(self, obj):
        return obj.get_publish_status_display()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    @staticmethod
    def tag_list(obj):
        return ', '.join(sorted(t.name for t in obj.tags.all()))

    def save_model(self, request, obj, form, change):
        if 'address' in form.changed_data:
            obj.latitude = None
            obj.longitude = None

        super().save_model(request, obj, form, change)

        if obj.address and 'address' in form.changed_data:
            transaction.on_commit(lambda: geocode_event(obj.pk, obj.address))


admin.site.register(Event, EventAdmin)
