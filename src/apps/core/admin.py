from django.contrib import admin

from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(UnfoldModelAdmin, SingletonModelAdmin):
    fieldsets = (
        ('Branding', {'fields': ('org_name', 'org_description', 'theme_color', 'facebook_app_id')}),
        ('Social links', {'fields': ('telegram_url', 'bluesky_url', 'x_url')}),
        ('Contact', {'fields': ('contact_email',)}),
    )
