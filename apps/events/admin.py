from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Event


class EventAdmin(ModelAdmin):
    list_display = ('title', 'start', 'tag_list')

    @staticmethod
    def tag_list(obj):
        return ", ".join(o.name for o in obj.tags.all().order_by('name'))


admin.site.register(Event, EventAdmin)
