from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.forms import PasswordInput
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from allauth.account.admin import EmailAddressAdmin as BaseEmailAddressAdmin
from allauth.account.models import EmailAddress
from allauth.idp.oidc.admin import ClientAdmin as BaseClientAdmin
from allauth.idp.oidc.models import Client
from allauth.mfa.admin import AuthenticatorAdmin as BaseAuthenticatorAdmin
from allauth.mfa.models import Authenticator
from allauth.socialaccount.admin import (
    SocialAccountAdmin as BaseSocialAccountAdmin,
)
from allauth.socialaccount.admin import (
    SocialTokenAdmin as BaseSocialTokenAdmin,
)
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import StackedInline, TabularInline
from unfold.decorators import action, display
from unfold.widgets import INPUT_CLASSES

from .models import ClientMetadata, User, Verification


class VerificationInline(StackedInline):
    model = Verification
    fk_name = 'user'
    extra = 0
    max_num = 1
    show_count = True
    readonly_fields = ('verified_at',)
    raw_id_fields = ('verified_by',)


class EmailAddressInline(TabularInline):
    model = EmailAddress
    extra = 0
    show_count = True
    hide_title = True
    fields = ('email', 'primary', 'verified')
    readonly_fields = ('email',)

    def has_add_permission(self, request, obj=None):
        return False


class AuthenticatorInline(TabularInline):
    model = Authenticator
    extra = 0
    show_count = True
    hide_title = True
    readonly_fields = ('type', 'created_at', 'last_used_at')
    fields = ('type', 'created_at', 'last_used_at')

    def has_add_permission(self, request, obj=None):
        return False


class UnfoldPasswordChangeForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, PasswordInput):
                field.widget.attrs['class'] = ' '.join(INPUT_CLASSES)


class HasMFAFilter(admin.SimpleListFilter):
    title = 'MFA'
    parameter_name = 'has_mfa'

    def lookups(self, request, model_admin):
        return [('yes', 'Enabled'), ('no', 'Disabled')]

    def queryset(self, request, queryset):
        from django.db.models import Exists, OuterRef

        subquery = Authenticator.objects.filter(user_id=OuterRef('pk')).exclude(type=Authenticator.Type.RECOVERY_CODES)
        if self.value() == 'yes':
            return queryset.filter(Exists(subquery))
        if self.value() == 'no':
            return queryset.exclude(Exists(subquery))
        return queryset


class IsVerifiedFilter(admin.SimpleListFilter):
    title = 'Verified'
    parameter_name = 'is_verified'

    def lookups(self, request, model_admin):
        return [('yes', 'Verified'), ('no', 'Unverified')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(verification__isnull=False)
        if self.value() == 'no':
            return queryset.filter(verification__isnull=True)
        return queryset


class CustomUserAdmin(UnfoldModelAdmin, UserAdmin):
    change_password_form = UnfoldPasswordChangeForm
    list_per_page = 25
    list_display = [
        'show_user',
        'full_name',
        'date_joined',
        'last_login',
        'is_active',
        'is_verified_display',
        'has_mfa_display',
    ]
    inlines = [EmailAddressInline, VerificationInline, AuthenticatorInline]
    actions = ['verify_users']
    actions_detail = ['verify_user', 'generate_recovery_codes']

    list_filter = ['is_active', 'groups', HasMFAFilter, IsVerifiedFilter]

    exclude = ('first_name', 'last_name')
    readonly_fields = ('email', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'is_active')}),
        ('Personal info', {'fields': ('full_name', 'date_of_birth')}),
        ('Avatar', {'fields': ('avatar', 'avatar_ppoi')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        (
            'Permissions',
            {
                'classes': ('collapse',),
                'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
    )

    @action(description='Verify User', icon='verified')
    def verify_user(self, request, object_id):
        user = User.objects.get(pk=object_id)
        Verification.objects.get_or_create(
            user=user,
            defaults={
                'verified_by': request.user,
                'verified_at': timezone.now(),
            },
        )
        messages.success(request, f'{user.username} has been verified.')
        return HttpResponseRedirect(reverse('admin:accounts_user_change', args=[object_id]))

    @action(description='Recovery Codes', icon='key')
    def generate_recovery_codes(self, request, object_id):
        from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes

        user = User.objects.get(pk=object_id)
        has_mfa = Authenticator.objects.filter(user=user).exclude(type=Authenticator.Type.RECOVERY_CODES).exists()
        if not has_mfa:
            messages.error(request, f'{user.username} does not have MFA enabled.')
            return HttpResponseRedirect(reverse('admin:accounts_user_change', args=[object_id]))

        rc = RecoveryCodes.activate(user)
        unused = rc.get_unused_codes()
        if unused:
            code_list = ', '.join(unused)
            messages.success(request, f'Recovery codes for {user.username}: {code_list}')
        else:
            Authenticator.objects.filter(user=user, type=Authenticator.Type.RECOVERY_CODES).delete()
            rc = RecoveryCodes.activate(user)
            code_list = ', '.join(rc.get_unused_codes())
            messages.success(request, f'New recovery codes for {user.username}: {code_list}')
        return HttpResponseRedirect(reverse('admin:accounts_user_change', args=[object_id]))

    @admin.action(description='Verify selected users')
    def verify_users(self, request, queryset):
        for user in queryset:
            Verification.objects.get_or_create(
                user=user,
                defaults={
                    'verified_by': request.user,
                    'verified_at': timezone.now(),
                },
            )
        messages.success(request, f'{queryset.count()} user(s) verified.')

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

    @admin.display(boolean=True, description='MFA')
    def has_mfa_display(self, obj):
        return obj._has_mfa

    def get_queryset(self, request):
        from django.db.models import Exists, OuterRef

        return (
            super()
            .get_queryset(request)
            .select_related('verification')
            .annotate(
                _has_mfa=Exists(
                    Authenticator.objects.filter(user_id=OuterRef('pk')).exclude(type=Authenticator.Type.RECOVERY_CODES)
                )
            )
        )


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


class CustomAuthenticatorAdmin(UnfoldModelAdmin, BaseAuthenticatorAdmin):
    pass


class CustomSocialAccountAdmin(UnfoldModelAdmin, BaseSocialAccountAdmin):
    pass


class CustomSocialTokenAdmin(UnfoldModelAdmin, BaseSocialTokenAdmin):
    list_display = ('account_link', 'truncated_token', 'expires_at')
    exclude = ('app',)

    @admin.display(description='Account')
    def account_link(self, obj):
        url = reverse('admin:socialaccount_socialtoken_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.account)


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Client)
admin.site.register(Client, CustomClientAdmin)
admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, CustomEmailAddressAdmin)
admin.site.unregister(Authenticator)
admin.site.register(Authenticator, CustomAuthenticatorAdmin)
admin.site.unregister(SocialAccount)
admin.site.register(SocialAccount, CustomSocialAccountAdmin)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.register(SocialToken, CustomSocialTokenAdmin)
