# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'name', 'date_joined', 'is_active']

    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


admin.site.register(User, CustomUserAdmin)
