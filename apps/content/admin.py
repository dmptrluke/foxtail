from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Page


class PageAdmin(SortableAdminMixin, ModelAdmin):  # lgtm [py/conflicting-attributes]
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'body')}),
        ('Advanced options', {'fields': ('slug', 'show_in_menu'),}),
    )

    list_display = ('title', 'slug', 'modified', 'show_in_menu')
    list_editable = ['show_in_menu']
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Page, PageAdmin)
