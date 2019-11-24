from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Event

admin.site.register(Event, ModelAdmin)
