from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from allauth.idp.oidc.admin import ClientAdmin as BaseClientAdmin
from allauth.idp.oidc.models import Client

from .models import ClientMetadata, User


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'full_name', 'date_joined', 'is_active']

    exclude = ('first_name', 'last_name')
    readonly_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'date_of_birth')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class ClientMetadataInline(admin.StackedInline):
    model = ClientMetadata
    extra = 1
    max_num = 1


class CustomClientAdmin(BaseClientAdmin):
    inlines = [ClientMetadataInline]


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Client)
admin.site.register(Client, CustomClientAdmin)
