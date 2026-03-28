from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from allauth.account.admin import EmailAddressAdmin as BaseEmailAddressAdmin
from allauth.account.models import EmailAddress
from allauth.idp.oidc.admin import ClientAdmin as BaseClientAdmin
from allauth.idp.oidc.models import Client
from allauth.mfa.models import Authenticator
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import StackedInline, TabularInline
from unfold.decorators import display

from .models import ClientMetadata, User, Verification


class VerificationInline(StackedInline):
    model = Verification
    fk_name = 'user'
    extra = 0
    max_num = 1
    show_count = True
    readonly_fields = ('verified_at',)
    raw_id_fields = ('verified_by',)


class AuthenticatorInline(TabularInline):
    model = Authenticator
    extra = 0
    show_count = True
    readonly_fields = ('type', 'created_at', 'last_used_at')
    fields = ('type', 'created_at', 'last_used_at')

    def has_add_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UnfoldModelAdmin, UserAdmin):
    list_display = ['show_user', 'full_name', 'date_joined', 'last_login', 'is_active', 'is_verified_display']
    inlines = [VerificationInline, AuthenticatorInline]

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

    @display(description='User', header=True, ordering='username')
    def show_user(self, obj):
        avatar = {'path': obj.avatar.url} if obj.avatar else None
        return [obj.username, obj.email, '', avatar]

    @admin.display(boolean=True, description='Verified')
    def is_verified_display(self, obj):
        try:
            return obj.verification is not None
        except Verification.DoesNotExist:
            return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('verification')


class ClientMetadataInline(StackedInline):
    model = ClientMetadata
    extra = 0
    max_num = 1
    show_count = True


class CustomClientAdmin(UnfoldModelAdmin, BaseClientAdmin):
    inlines = [ClientMetadataInline]


class CustomEmailAddressAdmin(UnfoldModelAdmin, BaseEmailAddressAdmin):
    list_display = ('email', 'user_link', 'primary', 'verified')

    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user)


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Client)
admin.site.register(Client, CustomClientAdmin)
admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, CustomEmailAddressAdmin)
