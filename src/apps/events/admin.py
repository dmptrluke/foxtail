from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin

from .models import Event


class EventAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'tags', 'description', 'url', 'publish_status', 'live_as_of')}),
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

    list_display = ('title', 'start', 'tag_list')

    @staticmethod
    def tag_list(obj):
        return ', '.join(o.name for o in obj.tags.all().order_by('name'))

    def save_model(self, request, obj, form, change):
        api_key = settings.MAPTILER_API_KEY
        address_changed = 'address' in form.changed_data

        if api_key and address_changed:
            if obj.address:
                from .maptiler import geocode

                coords = geocode(obj.address, api_key)
                if coords:
                    obj.latitude, obj.longitude = coords
                else:
                    messages.warning(request, 'Address could not be geocoded. Enter coordinates manually if needed.')
            else:
                obj.latitude = None
                obj.longitude = None

        super().save_model(request, obj, form, change)


admin.site.register(Event, EventAdmin)
