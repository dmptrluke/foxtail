from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Character

admin.site.register(Character, ModelAdmin)