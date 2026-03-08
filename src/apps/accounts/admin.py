from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from allauth.idp.oidc.admin import ClientAdmin as BaseClientAdmin
from allauth.idp.oidc.models import Client

from .models import ClientMetadata, User, Verification


class VerificationInline(admin.StackedInline):
    model = Verification
    fk_name = 'user'
    extra = 0
    max_num = 1
    readonly_fields = ('verified_at',)
    raw_id_fields = ('verified_by',)


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'full_name', 'date_joined', 'is_active', 'is_verified_display']
    inlines = [VerificationInline]

    exclude = ('first_name', 'last_name')
    readonly_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'date_of_birth')}),
        (
            'Permissions',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    @admin.display(boolean=True, description='Verified')
    def is_verified_display(self, obj):
        try:
            return obj.verification is not None
        except Verification.DoesNotExist:
            return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('verification')


class ClientMetadataInline(admin.StackedInline):
    model = ClientMetadata
    extra = 0
    max_num = 1


class CustomClientAdmin(BaseClientAdmin):
    inlines = [ClientMetadataInline]


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Client)
admin.site.register(Client, CustomClientAdmin)
