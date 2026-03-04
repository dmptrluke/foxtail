from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Event


class EventAdmin(ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'tags', 'description', 'url')
        }),
        ('Location', {
            'fields': ('location', 'address'),
        }),
        ('Time and Date', {
            'fields': ('start', 'start_time', 'end', 'end_time'),
        }),
        ('Image', {
            'fields': ('image',),
        }),
    )

    list_display = ('title', 'start', 'tag_list')

    @staticmethod
    def tag_list(obj):
        return ", ".join(o.name for o in obj.tags.all().order_by('name'))


admin.site.register(Event, EventAdmin)
