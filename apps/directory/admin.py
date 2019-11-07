from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Character

admin.site.register(Character, GuardedModelAdmin)
