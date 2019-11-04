# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    readonly_fields = ('username', 'display_name', 'email', 'profile_URL')
    ordering = ('display_name',)

    list_display = ['display_name', 'email', 'date_joined', 'is_active']

    fieldsets = (
        ('Login Server Data', {'fields': ('username', 'display_name', 'profile_URL', 'email')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
