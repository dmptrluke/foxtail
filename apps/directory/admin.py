from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from .models import Character, Profile

admin.site.register(Profile, GuardedModelAdmin)
admin.site.register(Character, GuardedModelAdmin)
