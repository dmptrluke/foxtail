from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Character, Profile

admin.site.register(Profile, ModelAdmin)
admin.site.register(Character, ModelAdmin)
