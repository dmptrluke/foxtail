from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import LinkToken, TelegramLink


@admin.register(TelegramLink)
class TelegramLinkAdmin(UnfoldModelAdmin):
    list_display = ['user', 'telegram_id', 'username', 'linked_at', 'is_blocked']
    search_fields = ['user__username', 'username', 'telegram_id']
    raw_id_fields = ['user']
    readonly_fields = ['linked_at']


@admin.register(LinkToken)
class LinkTokenAdmin(UnfoldModelAdmin):
    list_display = ['telegram_id', 'username', 'created_at', 'expires_at']
    readonly_fields = ['created_at']
