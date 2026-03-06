from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.core.files.base import ContentFile

from .models import Event


class EventAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'tags', 'description', 'url')}),
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
                'fields': ('image', 'map_image'),
            },
        ),
    )

    list_display = ('title', 'start', 'tag_list')

    @staticmethod
    def tag_list(obj):
        return ', '.join(o.name for o in obj.tags.all().order_by('name'))

    def save_model(self, request, obj, form, change):
        token = settings.MAPBOX_ACCESS_TOKEN
        address_changed = 'address' in form.changed_data
        coords_changed = 'latitude' in form.changed_data or 'longitude' in form.changed_data

        if token and address_changed:
            if obj.address:
                from .mapbox import geocode

                coords = geocode(obj.address, token)
                if coords:
                    obj.latitude, obj.longitude = coords
                    self._fetch_map(request, obj, token)
                else:
                    messages.warning(request, 'Address could not be geocoded. Enter coordinates manually if needed.')
            else:
                obj.latitude = None
                obj.longitude = None
                if obj.map_image:
                    obj.map_image.delete(save=False)

        elif token and coords_changed and not address_changed:
            if obj.latitude is not None and obj.longitude is not None:
                self._fetch_map(request, obj, token)
            elif obj.map_image:
                obj.map_image.delete(save=False)

        super().save_model(request, obj, form, change)

    @staticmethod
    def _fetch_map(request, obj, token):
        from .mapbox import static_map

        map_bytes = static_map(obj.latitude, obj.longitude, token)
        if map_bytes:
            filename = f'{obj.slug or "event"}-map.png'
            if obj.map_image:
                obj.map_image.delete(save=False)
            obj.map_image.save(filename, ContentFile(map_bytes), save=False)
        else:
            messages.warning(request, 'Map image could not be generated.')


admin.site.register(Event, EventAdmin)
