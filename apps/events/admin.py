from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Event

class EventAdmin(ModelAdmin):
    list_display = ('title', 'start')

admin.site.register(Event, EventAdmin)
