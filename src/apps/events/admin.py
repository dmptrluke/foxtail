from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db import transaction

from .models import Event, EventInterest
from .tasks import geocode_event


class EventInterestInline(admin.TabularInline):
    model = EventInterest
    extra = 0
    readonly_fields = ('user', 'status', 'created')


class EventAdmin(ModelAdmin):
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
                    'publish_status',
                    'live_as_of',
                ),
            },
        ),
        (
            'Location',
            {
                'fields': ('location', 'address', 'latitude', 'longitude'),
            },
        ),
        (
            'Time and Date',
            {
                'fields': ('start', 'start_time', 'end', 'end_time'),
            },
        ),
        (
            'Image',
            {
                'fields': ('image', 'image_ppoi'),
            },
        ),
    )

    inlines = [EventInterestInline]
    autocomplete_fields = ['organisation', 'series']
    search_fields = ['title']
    list_display = ('title', 'start', 'tag_list')

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
