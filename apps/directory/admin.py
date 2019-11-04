from django.contrib import admin
from django.contrib.admin import ModelAdmin

from guardian.admin import GuardedModelAdmin

from .models import Character

admin.site.register(Character, GuardedModelAdmin)
